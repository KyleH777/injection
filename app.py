"""
Intentionally Vulnerable Flask Application — SQL Injection Lab

WARNING: This application is PURPOSELY INSECURE. It exists solely for
authorized security testing and education. Never deploy on a production
system or expose to untrusted networks without proper controls.

Usage:
    python init_lab.py   # create staging.db first
    python app.py        # start the server on 0.0.0.0:5000
"""

import sqlite3
import os

from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "staging.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------------------------------------------------------ #
#  Routes
# ------------------------------------------------------------------ #


@app.route("/")
def index():
    return jsonify(
        {
            "lab": "SQL Injection Testing Lab",
            "database": "staging.db",
            "table": "accounts (id, username, password, secret_data)",
            "endpoints": {
                "GET /api/search?id=": "Vulnerable lookup — SQL injection via f-string",
            },
            "examples": {
                "normal": "/api/search?id=1",
                "union_extract": "/api/search?id=0 UNION SELECT id,username,password,secret_data FROM accounts--",
                "boolean_blind": "/api/search?id=1 AND 1=1--",
                "tautology": "/api/search?id=1 OR 1=1--",
            },
            "warning": "This app is intentionally vulnerable. For authorized testing only.",
        }
    )


@app.route("/api/search")
def search():
    """
    VULNERABLE ENDPOINT — demonstrates SQL injection via f-string.

    The 'id' parameter is interpolated directly into the query with no
    sanitization, parameterization, or input validation.
    """
    user_id = request.args.get("id", "")

    if not user_id:
        return jsonify({"error": "Missing required parameter: id"}), 400

    # ----- INSECURE: f-string query construction -----
    query = f"SELECT id, username, password, secret_data FROM accounts WHERE id = {user_id}"

    db = get_db()
    try:
        rows = db.execute(query).fetchall()
        results = [dict(row) for row in rows]

        return jsonify(
            {
                "query_executed": query,
                "results": results,
                "count": len(results),
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "query_executed": query,
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        db.close()


# ------------------------------------------------------------------ #
#  Entrypoint
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("[!] staging.db not found. Initialize it first:")
        print("    python init_lab.py")
        exit(1)

    print("=" * 55)
    print("  SQL Injection Lab — Vulnerable by Design")
    print("=" * 55)
    print(f"  Database : {DB_PATH}")
    print("  Endpoint : GET /api/search?id=<value>")
    print("  Listening: http://0.0.0.0:5000")
    print("=" * 55)
    print("  WARNING: Do NOT expose to untrusted networks.")
    print("=" * 55)

    app.run(host="0.0.0.0", port=5000, debug=True)
