from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from email.message import EmailMessage
import json
import os
import smtplib
import sqlite3
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "queries.db"
MAIL_TO = "karanahuja57226@gmail.com"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or MAIL_TO)


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def row_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "subject": row["subject"],
        "message": row["message"],
        "status": row["status"],
        "created_at": row["created_at"],
    }


def send_message_email(query):
    if not SMTP_USER or not SMTP_PASSWORD:
        return False

    email = EmailMessage()
    email["To"] = MAIL_TO
    email["From"] = SMTP_FROM
    email["Reply-To"] = query["email"]
    email["Subject"] = f"Portfolio message: {query['subject']}"
    email.set_content(
        "\n".join(
            [
                "New portfolio contact message",
                "",
                f"Name: {query['name']}",
                f"Email: {query['email']}",
                f"Subject: {query['subject']}",
                "",
                query["message"],
            ]
        )
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(email)

    return True


class PortfolioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        return json.loads(self.rfile.read(content_length).decode("utf-8"))

    def query_id_from_path(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) == 3 and parts[:2] == ["api", "queries"]:
            try:
                return int(parts[2])
            except ValueError:
                return None
        return None

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/queries":
            with get_connection() as connection:
                rows = connection.execute(
                    "SELECT * FROM queries ORDER BY created_at DESC"
                ).fetchall()
            self.send_json([row_to_dict(row) for row in rows])
            return

        query_id = self.query_id_from_path()
        if query_id is not None:
            with get_connection() as connection:
                row = connection.execute(
                    "SELECT * FROM queries WHERE id = ?", (query_id,)
                ).fetchone()
            if row is None:
                self.send_json({"error": "Query not found"}, 404)
                return
            self.send_json(row_to_dict(row))
            return

        super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/queries":
            self.send_json({"error": "Not found"}, 404)
            return

        data = self.read_json_body()
        required_fields = ["name", "email", "subject", "message"]
        if any(not str(data.get(field, "")).strip() for field in required_fields):
            self.send_json({"error": "All fields are required"}, 400)
            return

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO queries (name, email, subject, message)
                VALUES (?, ?, ?, ?)
                """,
                (
                    data["name"].strip(),
                    data["email"].strip(),
                    data["subject"].strip(),
                    data["message"].strip(),
                ),
            )
            row = connection.execute(
                "SELECT * FROM queries WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()

        query = row_to_dict(row)
        email_sent = False
        try:
            email_sent = send_message_email(query)
        except Exception as error:
            print(f"Email notification failed: {error}")

        query["email_sent"] = email_sent
        self.send_json(query, 201)

    def do_PUT(self):
        query_id = self.query_id_from_path()
        if query_id is None:
            self.send_json({"error": "Not found"}, 404)
            return

        data = self.read_json_body()
        allowed_fields = ["name", "email", "subject", "message", "status"]
        updates = [
            (field, str(data[field]).strip())
            for field in allowed_fields
            if field in data and str(data[field]).strip()
        ]
        if not updates:
            self.send_json({"error": "No valid fields to update"}, 400)
            return

        set_clause = ", ".join(f"{field} = ?" for field, _ in updates)
        values = [value for _, value in updates]

        with get_connection() as connection:
            cursor = connection.execute(
                f"UPDATE queries SET {set_clause} WHERE id = ?",
                values + [query_id],
            )
            if cursor.rowcount == 0:
                self.send_json({"error": "Query not found"}, 404)
                return
            row = connection.execute(
                "SELECT * FROM queries WHERE id = ?", (query_id,)
            ).fetchone()

        self.send_json(row_to_dict(row))

    def do_DELETE(self):
        query_id = self.query_id_from_path()
        if query_id is None:
            self.send_json({"error": "Not found"}, 404)
            return

        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM queries WHERE id = ?", (query_id,))

        if cursor.rowcount == 0:
            self.send_json({"error": "Query not found"}, 404)
            return

        self.send_json({"deleted": True, "id": query_id})


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("localhost", 8000), PortfolioHandler)
    print("Portfolio running at http://localhost:8000")
    print("Query API running at http://localhost:8000/api/queries")
    server.serve_forever()
