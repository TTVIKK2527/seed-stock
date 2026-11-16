import unittest
from unittest.mock import Mock
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from src.database import open_database
from src.service import StockService


class ReserveTests(unittest.TestCase):
    def setUp(self):
        self.engine = open_database("sqlite://")
        self.ids = Mock(side_effect=["seed-1", "reservation-1", "reservation-2"])
        self.stock = StockService(self.engine, Mock(return_value="2026-11-16T10:00:00Z"), self.ids)
        self.stock.add_seed("Tomat", 10)

    def tearDown(self): self.engine.dispose()

    def test_reserve_decrements_stock_and_records_reservation(self):
        result = self.stock.reserve("seed-1", 4)
        self.assertEqual(result["quantity"], 4)
        self.assertEqual(result["status"], "active")
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 6)
        self.assertEqual(self.stock.list_reservations(), [result])

    def test_insufficient_stock_changes_nothing(self):
        with self.assertRaisesRegex(ValueError, "piisa"): self.stock.reserve("seed-1", 11)
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 10)
        self.assertEqual(self.stock.list_reservations(), [])

    def test_reserve_exact_remaining_stock(self):
        self.stock.reserve("seed-1", 10)
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 0)
        with self.assertRaises(ValueError): self.stock.reserve("seed-1", 1)

    def test_invalid_quantities_and_missing_seed(self):
        for quantity in (0, -1, True, 1.5):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError): self.stock.reserve("seed-1", quantity)
        with self.assertRaises(ValueError): self.stock.reserve("missing", 1)

    def test_failed_insert_rolls_back_stock_decrement(self):
        self.stock.reserve("seed-1", 2)
        self.ids.side_effect = None
        self.ids.return_value = "reservation-1"
        with self.assertRaises(ValueError): self.stock.reserve("seed-1", 3)
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 8)

    def test_database_foreign_key_and_check_constraints(self):
        with self.assertRaises(IntegrityError):
            with self.engine.begin() as connection:
                connection.execute(text("INSERT INTO reservations (id,seed_id,quantity,status,created_at) VALUES ('r','missing',1,'active','now')"))
        with self.assertRaises(IntegrityError):
            with self.engine.begin() as connection:
                connection.execute(text("UPDATE seeds SET quantity=-1"))


if __name__ == "__main__": unittest.main()
