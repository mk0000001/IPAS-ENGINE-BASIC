"""Illustrative arithmetic with caller-supplied example rates."""

from decimal import Context, Decimal, localcontext
import re


def _number(value: str | int) -> Decimal:
    if type(value) not in (str, int) or not re.fullmatch(
        r'[0-9]{1,10}(?:\.[0-9]{1,9})?', str(value)
    ):
        raise ValueError('Use a nonnegative fixed-point string or integer')
    result = Decimal(str(value))
    if result > 1_000_000_000:
        raise ValueError('Input exceeds the example limit')
    return result


def illustrative_cost(
    duration_seconds: str | int,
    filament_grams: str | int,
    hourly_rate: str | int,
    material_rate_per_gram: str | int,
) -> Decimal:
    """Return seconds / 3600 * hourly rate + grams * material rate.

    All four inputs are supplied by the caller. The result has no currency
    or billing-rounding rules; division uses a 40-digit decimal context.
    """
    seconds, grams, hourly, per_gram = map(_number, (
        duration_seconds, filament_grams, hourly_rate, material_rate_per_gram
    ))
    with localcontext(Context(prec=40)):
        return seconds / 3600 * hourly + grams * per_gram
