#!/usr/bin/env python3
"""
Generate a readable HTML report from sqli_tester.py JSON output.

Usage:
    python sqli_tester.py --target http://127.0.0.1:5000 --all -o results.json
    python report.py results.json -o report.html
"""

import json
import sys
import argparse
from datetime import datetime


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SQL Injection Test Report</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0d1117; color: #c9d1d9; }}
  h1 {{ color: #58a6ff; }}
  h2 {{ color: #79c0ff; border-bottom: 1px solid #30363d; padding-bottom: 0.5rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
  th, td {{ border: 1px solid #30363d; padding: 8px 12px; text-align: left; }}
  th {{ background: #161b22; color: #8b949e; }}
  .success {{ background: #1a3a1a; color: #3fb950; }}
  .error {{ background: #3a1a1a; color: #f85149; }}
  .blocked {{ background: #161b22; }}
  .summary {{ background: #161b22; padding: 1rem; border-radius: 6px; margin-bottom: 2rem; }}
  .summary span {{ font-size: 1.5rem; font-weight: bold; }}
  code {{ background: #161b22; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
  .meta {{ color: #8b949e; font-size: 0.9em; }}
</style>
</head>
<body>
<h1>SQL Injection Test Report</h1>
<p class="meta">Generated: {timestamp}</p>

<div class="summary">
  <p>Categories tested: <span>{num_categories}</span></p>
  <p>Total payloads: <span>{total_payloads}</span></p>
  <p>Successful injections: <span style="color:#3fb950">{total_successes}</span></p>
  <p>Errors triggered: <span style="color:#f85149">{total_errors}</span></p>
</div>

{category_sections}
</body>
</html>"""


CATEGORY_SECTION = """
<h2>{category}</h2>
<p>{success_count} successful out of {total_count} payloads</p>
<table>
<tr><th>#</th><th>Payload</th><th>Status</th><th>Classification</th><th>Time (s)</th></tr>
{rows}
</table>
"""


def classify_css(classification):
    if "SUCCESS" in classification or "DELAYED" in classification:
        return "success"
    if "error" in classification:
        return "error"
    return "blocked"


def generate_report(data):
    sections = []
    total_payloads = 0
    total_successes = 0
    total_errors = 0

    for category, results in data.items():
        rows = []
        for i, r in enumerate(results, 1):
            css = classify_css(r["classification"])
            payload_escaped = (
                r["payload"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            rows.append(
                f'<tr class="{css}"><td>{i}</td><td><code>{payload_escaped}</code></td>'
                f'<td>{r["status_code"]}</td><td>{r["classification"]}</td>'
                f'<td>{r["elapsed"]}</td></tr>'
            )

        successes = sum(1 for r in results if "SUCCESS" in r["classification"] or "DELAYED" in r["classification"])
        errors = sum(1 for r in results if "error" in r["classification"])
        total_payloads += len(results)
        total_successes += successes
        total_errors += errors

        sections.append(
            CATEGORY_SECTION.format(
                category=category,
                success_count=successes,
                total_count=len(results),
                rows="\n".join(rows),
            )
        )

    return HTML_TEMPLATE.format(
        timestamp=datetime.now().isoformat(),
        num_categories=len(data),
        total_payloads=total_payloads,
        total_successes=total_successes,
        total_errors=total_errors,
        category_sections="\n".join(sections),
    )


def main():
    parser = argparse.ArgumentParser(description="Generate SQLi test report")
    parser.add_argument("input", help="JSON results file from sqli_tester.py")
    parser.add_argument("-o", "--output", default="report.html", help="Output HTML file")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    html = generate_report(data)

    with open(args.output, "w") as f:
        f.write(html)

    print(f"Report generated: {args.output}")
    print(f"  Categories: {len(data)}")
    total = sum(len(v) for v in data.values())
    print(f"  Total payloads: {total}")


if __name__ == "__main__":
    main()
