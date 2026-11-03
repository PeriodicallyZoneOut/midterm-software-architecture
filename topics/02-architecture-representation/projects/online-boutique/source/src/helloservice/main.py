"""Read greetings from the Hello service's dedicated MariaDB database."""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class GreetingNotFound(Exception):
    pass


def connect_database():
    import pymysql

    return pymysql.connect(
        host=os.environ.get("DB_HOST", "hello-db"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "hello"),
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "hello"),
        charset="utf8mb4",
        autocommit=True,
        connect_timeout=2,
        read_timeout=2,
        write_timeout=2,
    )


def read_greeting():
    # Each request gets a connection: do not share connections across HTTP threads.
    with connect_database() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT message FROM greetings WHERE id = %s", (1,))
            row = cursor.fetchone()
    if row is None:
        raise GreetingNotFound()
    return row[0]


class HelloHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self.send_json(200, {"status": "ok"})
            return
        if self.path not in {"/hello", "/readyz"}:
            self.send_json(404, {"error": "Not found"})
            return
        try:
            message = read_greeting()
        except GreetingNotFound:
            self.send_json(404 if self.path == "/hello" else 503,
                           {"error": "Greeting not found"})
        except Exception:
            logging.exception("Could not read the greeting from MariaDB")
            self.send_json(503, {"error": "Greeting database is unavailable"})
        else:
            payload = {"message": message} if self.path == "/hello" else {"status": "ready"}
            self.send_json(200, payload)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = ThreadingHTTPServer((os.environ.get("LISTEN_ADDR", "0.0.0.0"),
                                 int(os.environ.get("PORT", "8080"))), HelloHandler)
    logging.info("Hello service listening on port %s", server.server_port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
