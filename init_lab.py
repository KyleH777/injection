"""
Initialize the SQL Injection Testing Lab database.

Creates staging.db with an 'accounts' table and populates it with
5 dummy records for authorized security testing.

Usage:
    python init_lab.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "staging.db")


def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[*] Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            secret_data TEXT NOT NULL
        )
        """
    )

    dummy_records = [
        ("admin", "admin123", "FLAG{admin_secret_2024}"),
        ("jdoe", "p@ssw0rd!", "SSN: 123-45-6789"),
        ("alice", "alice.secret", "API_KEY=sk-live-abc123xyz"),
        ("bob", "b0bBuilds!", "DB_CONN=postgres://prod:secret@10.0.0.5/core"),
        ("svc_deploy", "deploy#Token9", "AWS_SECRET=wJalrXUtnFEMI/K7MDENG/bPxRfi"),
    ]

    cursor.executemany(
        "INSERT INTO accounts (username, password, secret_data) VALUES (?, ?, ?)",
        dummy_records,
    )

    conn.commit()
    conn.close()

    print(f"[+] Database created: {DB_PATH}")
    print(f"[+] Table 'accounts' populated with {len(dummy_records)} records:")
    print()
    print(f"    {'ID':<4} {'Username':<14} {'Password':<18} {'Secret Data'}")
    print(f"    {'—'*4} {'—'*14} {'—'*18} {'—'*35}")
    for i, (user, pwd, secret) in enumerate(dummy_records, 1):
        print(f"    {i:<4} {user:<14} {pwd:<18} {secret}")
    print()
    print("[*] Run 'python app.py' to start the vulnerable Flask server.")


if __name__ == "__main__":
    init_db()
