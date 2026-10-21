import io
from decimal import Decimal
import unittest

from ipas_gcode_basic import read_header
from ipas_cost_basic import illustrative_cost


class HeaderTests(unittest.TestCase):
    def read(self, content):
        return read_header(io.BytesIO(content))

    def test_simple_header(self):
        result = self.read(b';TIME:3600\n; filament used [g] = 12.50\n; filament_type = PLA\nG28\n')
        self.assertEqual(result.duration_seconds, 3600)
        self.assertEqual(result.filament_grams, Decimal('12.50'))
        self.assertEqual(result.materials, ('PLA',))

    def test_time_units_and_material_labels(self):
        result = self.read(b'; estimated printing time (normal mode) = 1d 2h 3m 4s\n; filament_type = PLA; PETG\n')
        self.assertEqual(result.duration_seconds, 93784)
        self.assertEqual(result.materials, ('PLA', 'PETG'))

    def test_stops_before_commands_and_ignores_footer(self):
        result = self.read(b'; unrelated comment\n\nG1 X10 E1\n;TIME:99\n; filament used [g] = 5\n')
        self.assertIsNone(result.duration_seconds)
        self.assertIsNone(result.filament_grams)
        self.assertEqual(result.materials, ())

    def test_no_motion_inference(self):
        result = self.read(b'G1 X10 Y20 E100 F60\n')
        self.assertIsNone(result.duration_seconds)
        self.assertIsNone(result.filament_grams)

    def test_conflicting_duplicates_are_rejected(self):
        for content in (b';TIME:10\n;TIME:20\n', b'; filament used [g] = 1\n; filament used [g] = 2\n'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.read(content)

    def test_invalid_recognized_values_are_rejected(self):
        for value in (b'-1', b'NaN', b'Infinity', b'1e100', b'1, 2', b'1e-1000000'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.read(b'; filament used [g] = ' + value + b'\n')
        for value in (b'-1', b'1.5', b'999999999999999999999999999999999'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.read(b';TIME:' + value + b'\n')

    def test_resource_limits_and_binary_input(self):
        for content in (b';' + b'x' * 4096, b';' + b'x' * 1000 + b'\n' * 70000, b';\x00\n', b'PK\x03\x04', b';\xff\n'):
            with self.subTest(size=len(content)), self.assertRaises(ValueError):
                self.read(content)


class CostTests(unittest.TestCase):
    def test_exact_arithmetic(self):
        self.assertEqual(illustrative_cost('3600', '12.5', '2', '0.04'), Decimal('2.500'))

    def test_zero_is_valid(self):
        self.assertEqual(illustrative_cost('0', '0', '0', '0'), Decimal('0'))

    def test_rejects_invalid_and_ambiguous_inputs(self):
        for value in (True, 0.1, None, '-1', 'NaN', 'Infinity', '1e100000', '1e-1000000', '1000000001'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                illustrative_cost(value, '1', '1', '1')

    def test_cost_does_not_depend_on_callers_decimal_context(self):
        from decimal import ROUND_DOWN, localcontext
        with localcontext() as context:
            context.prec = 2
            context.rounding = ROUND_DOWN
            context.Emax = 2
            context.Emin = -2
            self.assertEqual(illustrative_cost('3600', '12.5', '2', '0.04'), Decimal('2.500'))
            self.assertEqual(
                illustrative_cost('1', '0', '1', '0'),
                Decimal('0.0002777777777777777777777777777777777777778'),
            )


if __name__ == '__main__':
    unittest.main()
