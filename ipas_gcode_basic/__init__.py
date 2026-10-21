"""A small reader for explicit metadata in leading G-code comments."""

from dataclasses import dataclass
from decimal import Decimal
import re
from typing import BinaryIO


@dataclass(frozen=True)
class HeaderMetadata:
    duration_seconds: int | None = None
    filament_grams: Decimal | None = None
    materials: tuple[str, ...] = ()


_TIME = re.compile(r'TIME\s*:\s*(.*)', re.IGNORECASE)
_ESTIMATE = re.compile(
    r'estimated printing time(?: \(normal mode\))?\s*=\s*(.*)', re.IGNORECASE
)
_MASS = re.compile(r'filament used \[g\]\s*=\s*(.*)', re.IGNORECASE)
_MATERIAL = re.compile(r'filament_type\s*=\s*(.*)', re.IGNORECASE)


def _seconds(value: str, with_units: bool) -> int:
    if with_units:
        match = re.fullmatch(
            r'(?:(\d{1,9})d\s*)?(?:(\d{1,9})h\s*)?'
            r'(?:(\d{1,9})m\s*)?(?:(\d{1,9})s\s*)?', value
        )
        if not match or not any(match.groups()):
            raise ValueError('Invalid declared time')
        result = sum(int(number or '0') * unit for number, unit in zip(
            match.groups(), (86400, 3600, 60, 1)
        ))
    else:
        if not re.fullmatch(r'\d{1,10}', value):
            raise ValueError('Invalid declared time')
        result = int(value)
    if result > 1_000_000_000:
        raise ValueError('Declared time exceeds the example limit')
    return result


def read_header(stream: BinaryIO) -> HeaderMetadata:
    """Read at most 64 KiB of leading comments; stop at the first command.

    Each line is limited to 4096 bytes. Only the four documented comment
    formats are recognized. Values are declarations, not measured facts.
    """
    values = {}
    consumed = 0
    while True:
        raw = stream.readline(4097)
        if not raw:
            break
        consumed += len(raw)
        if len(raw) > 4096 or consumed > 65536:
            raise ValueError('Header resource limit exceeded')
        if b'\x00' in raw or raw.startswith(b'PK'):
            raise ValueError('Expected plain UTF-8 G-code')
        try:
            text = raw.decode('utf-8').strip()
        except UnicodeDecodeError as exc:
            raise ValueError('Expected plain UTF-8 G-code') from exc
        if not text:
            continue
        if not text.startswith(';'):
            break
        comment = text[1:].strip()
        if match := _TIME.fullmatch(comment):
            key, value = 'duration_seconds', _seconds(match[1], False)
        elif match := _ESTIMATE.fullmatch(comment):
            key, value = 'duration_seconds', _seconds(match[1], True)
        elif match := _MASS.fullmatch(comment):
            if not re.fullmatch(r'\d{1,10}(?:\.\d{1,9})?', match[1]):
                raise ValueError('Expected a single nonnegative filament mass')
            key, value = 'filament_grams', Decimal(match[1])
            if value > 1_000_000_000:
                raise ValueError('Declared mass exceeds the example limit')
        elif match := _MATERIAL.fullmatch(comment):
            labels = tuple(part.strip() for part in re.split(r'[,;]', match[1]))
            if len(labels) > 16 or not all(
                re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 ._+()/\-]{0,63}', label)
                for label in labels
            ):
                raise ValueError('Invalid material labels')
            key, value = 'materials', labels
        else:
            continue
        if key in values and values[key] != value:
            raise ValueError('Conflicting declared header values')
        values[key] = value
    return HeaderMetadata(**values)
