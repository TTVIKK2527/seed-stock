import unittest
from unittest.mock import Mock
from src.database import open_database
from src.service import StockService


class RegisterTests(unittest.TestCase):
    def setUp(self):
        self.engine = open_database("sqlite://")
        self.clock = Mock(return_value="2026-11-16T10:00:00Z")
        self.ids = Mock(return_value="seed-1")
        self.stock = StockService(self.engine, self.clock, self.ids)

    def tearDown(self): self.engine.dispose()

    def test_register_stores_name_quantity_and_injected_time(self):
        result = self.stock.add_seed("  Tomat  ", 10)
        self.assertEqual(result, {"id": "seed-1", "name": "Tomat", "quantity": 10, "createdAt": self.clock.return_value})
        self.assertEqual(self.stock.list_seeds(), [result])
        self.clock.assert_called_once_with()
        self.ids.assert_called_once_with()

    def test_duplicate_name_is_rejected_even_with_different_case(self):
        self.stock.add_seed("Tomat", 10)
        with self.assertRaisesRegex(ValueError, "juba"):
            self.stock.add_seed(" TOMAT ", 5)
        self.assertEqual(len(self.stock.list_seeds()), 1)

    def test_empty_name_rejected(self):
        for name in ("", "  ", None):
            with self.subTest(name=name), self.assertRaises(ValueError): self.stock.add_seed(name, 1)

    def test_invalid_quantities_rejected(self):
        for amount in (-1, 1.5, "1", True, None):
            with self.subTest(amount=amount), self.assertRaises(ValueError): self.stock.add_seed("Tomat", amount)

    def test_zero_quantity_is_allowed(self):
        self.assertEqual(self.stock.add_seed("Tomat", 0)["quantity"], 0)


if __name__ == "__main__": unittest.main()
