"""Run from the repository root: python -B -m examples.basic_usage"""

from pathlib import Path

from ipas_cost_basic import illustrative_cost
from ipas_gcode_basic import read_header


def main():
    with Path(__file__).with_name('sample.gcode').open('rb') as stream:
        metadata = read_header(stream)
    print('Declared duration in seconds:', metadata.duration_seconds)
    print('Declared filament in grams:', metadata.filament_grams)
    print('Declared material labels:', ', '.join(metadata.materials))
    # Arbitrary teaching values, expressed in unspecified currency units.
    if metadata.duration_seconds is not None and metadata.filament_grams is not None:
        result = illustrative_cost(
            str(metadata.duration_seconds), str(metadata.filament_grams), '2', '0.04'
        )
        print('Illustrative arithmetic result:', result)


if __name__ == '__main__':
    main()
