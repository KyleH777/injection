"""
Intentionally Vulnerable Flask Application for SQL Injection Testing.

WARNING: This application is PURPOSELY INSECURE. Never deploy it on a
network accessible to others. Run only on localhost for learning/testing.
"""

import sqlite3
import os

from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Vulnerable Endpoints ----------


@app.route("/")
def index():
    return jsonify(
        {
            "app": "SQL Injection Testing Lab",
            "endpoints": {
                "POST /login": "Auth bypass testing (params: username, password)",
                "GET /search?q=": "Union/error-based testing",
                "GET /user?id=": "Blind boolean/time-based testing",
                "GET /users": "List all users (for verification)",
            },
            "warning": "This app is intentionally vulnerable. Do not expose to a network.",
        }
    )


@app.route("/login", methods=["POST"])
def login():
    """VULNERABLE: Authentication bypass via string concatenation."""
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # INSECURE: Direct string formatting — vulnerable to SQLi
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

    db = get_db()
    try:
        result = db.execute(query).fetchone()
        if result:
            return jsonify(
                {
                    "status": "success",
                    "message": f"Welcome, {result['username']}!",
                    "role": result["role"],
                    "query_executed": query,
                }
            )
        else:
            return jsonify(
                {
                    "status": "failure",
                    "message": "Invalid credentials",
                    "query_executed": query,
                }
            ), 401
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "query_executed": query}), 500
    finally:
        db.close()


@app.route("/search")
def search():
    """VULNERABLE: Union-based and error-based injection via search."""
    q = request.args.get("q", "")

    # INSECURE: Direct string concatenation
    query = f"SELECT id, name, description, price FROM products WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"

    db = get_db()
    try:
        rows = db.execute(query).fetchall()
        results = [dict(row) for row in rows]
        return jsonify(
            {"results": results, "count": len(results), "query_executed": query}
        )
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "query_executed": query}), 500
    finally:
        db.close()


@app.route("/user")
def user_lookup():
    """VULNERABLE: Blind boolean and time-based injection."""
    user_id = request.args.get("id", "")

    # INSECURE: Direct string concatenation
    query = f"SELECT id, username, role FROM users WHERE id={user_id}"

    db = get_db()
    try:
        result = db.execute(query).fetchone()
        if result:
            return jsonify({"found": True, "user": dict(result), "query_executed": query})
        else:
            return jsonify({"found": False, "query_executed": query})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "query_executed": query}), 500
    finally:
        db.close()


@app.route("/users")
def list_users():
    """List users (for verifying injection results)."""
    db = get_db()
    try:
        rows = db.execute("SELECT id, username, role, email FROM users").fetchall()
        return jsonify({"users": [dict(r) for r in rows]})
    finally:
        db.close()


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Database not found. Run setup_db.py first:")
        print("  python setup_db.py")
        exit(1)
    print("=== SQL Injection Testing Lab ===")
    print("WARNING: This app is intentionally vulnerable!")
    print("Endpoints: /login  /search  /user  /users")
    print("=================================")
    app.run(debug=True, host="127.0.0.1", port=5000)
