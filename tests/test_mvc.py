import unittest
from unittest.mock import Mock
from src.app import create_app
from src.database import open_database
from src.service import StockService


class MvcTests(unittest.TestCase):
    def setUp(self):
        self.engine = open_database("sqlite://")
        self.stock = StockService(self.engine, Mock(return_value="now"), Mock(side_effect=["s1", "r1"]))
        self.app = create_app(stock=self.stock)
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()
        self.client.get("/")
        with self.client.session_transaction() as session: self.csrf = session["csrf"]

    def tearDown(self): self.engine.dispose()

    def test_empty_list_is_rendered_by_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Seemneid pole veel lisatud", response.get_data(as_text=True))

    def test_add_reserve_cancel_complete_workflow(self):
        self.assertEqual(self.client.post("/seeds", data={"name": "Tomat", "quantity": "5", "csrf": self.csrf}).status_code, 303)
        self.assertEqual(self.client.post("/reservations", data={"seedId": "s1", "quantity": "2", "csrf": self.csrf}).status_code, 303)
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 3)
        self.assertEqual(self.client.post("/reservations/r1/cancel", data={"csrf": self.csrf}).status_code, 303)
        self.assertEqual(self.stock.list_seeds()[0]["quantity"], 5)

    def test_invalid_input_is_visible_and_does_not_write(self):
        response = self.client.post("/seeds", data={"name": "Tomat", "quantity": "-1", "csrf": self.csrf})
        self.assertEqual(response.status_code, 400)
        self.assertIn('role="alert"', response.get_data(as_text=True))
        self.assertEqual(self.stock.list_seeds(), [])

    def test_names_are_html_escaped(self):
        self.stock.add_seed("<script>alert(1)</script>", 2)
        response = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("<script>alert(1)</script>", response)
        self.assertIn("&lt;script&gt;", response)

    def test_post_without_csrf_rejected(self):
        self.assertEqual(self.client.post("/seeds", data={"name": "Tomat", "quantity": "5"}).status_code, 400)
        self.assertEqual(self.stock.list_seeds(), [])


if __name__ == "__main__": unittest.main()
