"""Set up the SQLite database with sample data for testing."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")


def setup():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            email TEXT
        );

        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT
        );

        CREATE TABLE secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flag TEXT NOT NULL
        );

        -- Sample users (passwords are intentionally plaintext for testing)
        INSERT INTO users (username, password, role, email) VALUES
            ('admin', 's3cur3_adm1n_pw', 'admin', 'admin@example.com'),
            ('alice', 'alice_password', 'user', 'alice@example.com'),
            ('bob', 'bob_password', 'user', 'bob@example.com'),
            ('charlie', 'charlie_pass', 'moderator', 'charlie@example.com');

        -- Sample products
        INSERT INTO products (name, description, price, category) VALUES
            ('Laptop', 'High-performance laptop', 999.99, 'electronics'),
            ('Keyboard', 'Mechanical keyboard', 79.99, 'electronics'),
            ('Desk', 'Standing desk', 349.99, 'furniture'),
            ('Monitor', '27 inch 4K display', 449.99, 'electronics'),
            ('Chair', 'Ergonomic office chair', 299.99, 'furniture');

        -- Hidden flag for CTF-style challenges
        INSERT INTO secrets (flag) VALUES
            ('FLAG{sql_injection_master}');
        """
    )

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")
    print("Users: admin, alice, bob, charlie")
    print("Tables: users, products, secrets")


if __name__ == "__main__":
    setup()
