import pathlib
import tempfile
import unittest
from unittest.mock import Mock
from src.database import open_database, migrate
from src.service import StockService


class CancelTests(unittest.TestCase):
    def setUp(self):
        self.engine = open_database("sqlite://")
        self.clock = Mock(return_value="2026-11-16T10:00:00Z")
        self.stock = StockService(self.engine, self.clock, Mock(side_effect=["s1", "r1"]))
        self.stock.add_seed("Tomat", 10)
        self.stock.reserve("s1", 4)

    def tearDown(self): self.engine.dispose()

    def test_cancel_restores_stock_and_sets_time(self):
        self.clock.return_value = "2026-11-16T11:00:00Z"
        result = self.stock.cancel("r1")
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["cancelledAt"], self.clock.return_value)
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 10)

    def test_double_cancel_never_restores_stock_twice(self):
        self.stock.cancel("r1")
        with self.assertRaises(ValueError): self.stock.cancel("r1")
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 10)

    def test_missing_reservation_changes_nothing(self):
        with self.assertRaises(ValueError): self.stock.cancel("missing")
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 6)

    def test_migrations_and_rows_survive_reopening_database(self):
        with tempfile.TemporaryDirectory() as directory:
            url = "sqlite:///" + str(pathlib.Path(directory) / "test.db")
            engine = open_database(url)
            stock = StockService(engine, self.clock, Mock(side_effect=["seed", "reservation"]))
            stock.add_seed("Salat", 5)
            stock.reserve("seed", 2)
            engine.dispose()
            engine = open_database(url)
            try:
                migrate(engine)
                stock = StockService(engine, self.clock)
                self.assertEqual(stock.list_seeds()[0]["quantity"], 3)
                stock.cancel("reservation")
                self.assertEqual(stock.list_seeds()[0]["quantity"], 5)
            finally: engine.dispose()


if __name__ == "__main__": unittest.main()
