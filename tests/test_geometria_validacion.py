"""Regression tests for COM coordinate rounding, without PowerDesigner."""
import unittest
from geometria_validacion import coordenadas_coinciden


class TestCoordenadasCoinciden(unittest.TestCase):
    def test_exact_match(self):
        self.assertTrue(coordenadas_coinciden({"x": 9000, "y": 9500}, {"x": 9000, "y": 9500}))

    def test_com_rounding_one_unit_each_axis(self):
        self.assertTrue(coordenadas_coinciden({"x": 8999, "y": 9500}, {"x": 9000, "y": 9500}))
        self.assertTrue(coordenadas_coinciden({"x": -3273, "y": 4849}, {"x": -3274, "y": 4850}))

    def test_larger_differences_rejected(self):
        self.assertFalse(coordenadas_coinciden({"x": 8998, "y": 9500}, {"x": 9000, "y": 9500}))
        self.assertFalse(coordenadas_coinciden({"x": 9000, "y": 9502}, {"x": 9000, "y": 9500}))

    def test_missing_or_invalid_values_rejected(self):
        self.assertFalse(coordenadas_coinciden({"x": 9000}, {"x": 9000, "y": 9500}))
        self.assertFalse(coordenadas_coinciden({"x": 9000.0, "y": 9500}, {"x": 9000, "y": 9500}))
        self.assertFalse(coordenadas_coinciden({"x": True, "y": 9500}, {"x": 1, "y": 9500}))
        self.assertFalse(coordenadas_coinciden(None, {"x": 9000, "y": 9500}))

    def test_strict_mode(self):
        self.assertFalse(coordenadas_coinciden({"x": 8999, "y": 9500}, {"x": 9000, "y": 9500}, tolerancia=0))


if __name__ == "__main__":
    unittest.main()
