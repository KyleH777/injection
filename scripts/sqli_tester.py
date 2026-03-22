#!/usr/bin/env python3
"""
Automated SQL Injection Tester

Loads payloads from the payloads/ directory and fires them at the
vulnerable test application, reporting which ones succeed.

Usage:
    python sqli_tester.py --target http://127.0.0.1:5000
    python sqli_tester.py --target http://127.0.0.1:5000 --category auth-bypass
    python sqli_tester.py --target http://127.0.0.1:5000 --all
"""

import argparse
import os
import sys
import time
import urllib.parse
import json

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

PAYLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "payloads")

CATEGORY_ENDPOINT_MAP = {
    "auth-bypass": {"endpoint": "/login", "method": "POST"},
    "union-based": {"endpoint": "/search", "method": "GET"},
    "error-based": {"endpoint": "/search", "method": "GET"},
    "blind-boolean": {"endpoint": "/user", "method": "GET"},
    "blind-time": {"endpoint": "/user", "method": "GET"},
    "stacked-queries": {"endpoint": "/search", "method": "GET"},
}


def load_payloads(category):
    """Load payloads from a category file, skipping comments and blank lines."""
    filepath = os.path.join(PAYLOADS_DIR, f"{category}.txt")
    if not os.path.exists(filepath):
        print(f"  [!] Payload file not found: {filepath}")
        return []

    payloads = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                payloads.append(line)
    return payloads


def send_request(target, endpoint, method, payload):
    """Send a test request and return (status_code, response_body, elapsed)."""
    url = f"{target}{endpoint}"
    start = time.time()

    try:
        if method == "POST" and endpoint == "/login":
            data = urllib.parse.urlencode(
                {"username": payload, "password": payload}
            ).encode()
            req = urllib.request.Request(url, data=data)
        else:
            param = "q" if endpoint == "/search" else "id"
            url = f"{url}?{param}={urllib.parse.quote(payload)}"
            req = urllib.request.Request(url)

        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            elapsed = time.time() - start
            return resp.status, body, elapsed
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        elapsed = time.time() - start
        return e.code, body, elapsed
    except urllib.error.URLError as e:
        elapsed = time.time() - start
        return 0, str(e), elapsed
    except Exception as e:
        elapsed = time.time() - start
        return 0, str(e), elapsed


def classify_result(category, status, body, elapsed):
    """Determine if an injection was successful."""
    if status == 0:
        return "error"

    if category == "auth-bypass":
        if '"status": "success"' in body or '"status":"success"' in body:
            return "SUCCESS"
        if '"error"' in body:
            return "error-triggered"
        return "blocked"

    if category in ("union-based", "stacked-queries"):
        try:
            data = json.loads(body)
            if "error" in data:
                return "error-triggered"
            results = data.get("results", [])
            if len(results) > 0:
                return "SUCCESS"
        except json.JSONDecodeError:
            pass
        return "blocked"

    if category == "error-based":
        if '"error"' in body:
            return "error-triggered"
        return "no-error"

    if category == "blind-boolean":
        if '"found": true' in body or '"found":true' in body:
            return "true-response"
        if '"error"' in body:
            return "error-triggered"
        return "false-response"

    if category == "blind-time":
        if elapsed > 4.0:
            return "DELAYED (likely successful)"
        return f"fast ({elapsed:.1f}s)"

    return "unknown"


def run_category(target, category, verbose=False):
    """Test all payloads for a given category."""
    config = CATEGORY_ENDPOINT_MAP.get(category)
    if not config:
        print(f"  [!] No endpoint mapping for category: {category}")
        return []

    payloads = load_payloads(category)
    if not payloads:
        return []

    print(f"\n{'='*60}")
    print(f"  Category: {category}")
    print(f"  Endpoint: {config['method']} {config['endpoint']}")
    print(f"  Payloads: {len(payloads)}")
    print(f"{'='*60}")

    results = []
    for i, payload in enumerate(payloads, 1):
        status, body, elapsed = send_request(
            target, config["endpoint"], config["method"], payload
        )
        classification = classify_result(category, status, body, elapsed)

        is_success = "SUCCESS" in classification or "DELAYED" in classification or "error-triggered" in classification
        marker = "[+]" if is_success else "[-]"

        if verbose or is_success:
            truncated = payload[:60] + ("..." if len(payload) > 60 else "")
            print(f"  {marker} [{i}/{len(payloads)}] {classification:20s} | {truncated}")

        results.append(
            {
                "payload": payload,
                "status_code": status,
                "classification": classification,
                "elapsed": round(elapsed, 2),
            }
        )

    successes = sum(1 for r in results if "SUCCESS" in r["classification"] or "DELAYED" in r["classification"])
    errors = sum(1 for r in results if "error" in r["classification"])
    print(f"\n  Summary: {successes} successful, {errors} errors triggered, {len(results)} total")

    return results


def main():
    parser = argparse.ArgumentParser(description="SQL Injection Tester")
    parser.add_argument("--target", default="http://127.0.0.1:5000", help="Target base URL")
    parser.add_argument("--category", help="Specific category to test (e.g. auth-bypass)")
    parser.add_argument("--all", action="store_true", help="Test all categories")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all results, not just successes")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    args = parser.parse_args()

    print(f"SQL Injection Tester")
    print(f"Target: {args.target}")

    all_results = {}

    if args.category:
        categories = [args.category]
    elif args.all:
        categories = list(CATEGORY_ENDPOINT_MAP.keys())
    else:
        categories = list(CATEGORY_ENDPOINT_MAP.keys())

    for cat in categories:
        results = run_category(args.target, cat, verbose=args.verbose)
        all_results[cat] = results

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to {args.output}")

    # Print final summary
    print(f"\n{'='*60}")
    print("  FINAL SUMMARY")
    print(f"{'='*60}")
    for cat, results in all_results.items():
        successes = sum(1 for r in results if "SUCCESS" in r["classification"] or "DELAYED" in r["classification"])
        print(f"  {cat:20s}: {successes}/{len(results)} successful injections")


if __name__ == "__main__":
    main()
