import unittest
from unittest.mock import MagicMock, patch

import main


class GreetingTests(unittest.TestCase):
    @patch("main.connect_database")
    def test_reads_current_row_and_closes_connection(self, connect):
        connection = connect.return_value.__enter__.return_value
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = ("A greeting changed in MariaDB",)
        self.assertEqual(main.read_greeting(), "A greeting changed in MariaDB")
        cursor.execute.assert_called_once_with(
            "SELECT message FROM greetings WHERE id = %s", (1,))
        connect.return_value.__exit__.assert_called_once()

    @patch("main.connect_database")
    def test_missing_row_is_not_replaced_with_a_hardcoded_greeting(self, connect):
        cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = None
        with self.assertRaises(main.GreetingNotFound):
            main.read_greeting()

    def request(self, path):
        handler = object.__new__(main.HelloHandler)
        handler.path = path
        handler.send_json = MagicMock()
        handler.do_GET()
        return handler.send_json.call_args.args

    @patch("main.read_greeting", return_value="Hello world!")
    def test_hello_returns_database_value(self, read):
        self.assertEqual(self.request("/hello"), (200, {"message": "Hello world!"}))
        read.assert_called_once()

    @patch("main.read_greeting", side_effect=RuntimeError("private database details"))
    def test_database_failure_is_503_without_leaking_details(self, _read):
        with self.assertLogs(level="ERROR"):
            status, payload = self.request("/hello")
        self.assertEqual(status, 503)
        self.assertEqual(payload, {"error": "Greeting database is unavailable"})

    @patch("main.read_greeting", side_effect=main.GreetingNotFound)
    def test_missing_greeting_and_readiness_fail(self, _read):
        self.assertEqual(self.request("/hello")[0], 404)
        self.assertEqual(self.request("/readyz")[0], 503)

    @patch("main.read_greeting")
    def test_liveness_does_not_require_database(self, read):
        self.assertEqual(self.request("/healthz"), (200, {"status": "ok"}))
        self.assertEqual(self.request("/unknown")[0], 404)
        read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
