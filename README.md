# SQL Injection Security Testing Lab

## Educational Objective

This repository is a **hands-on learning lab** for understanding, detecting, and preventing SQL injection vulnerabilities. It is designed for cybersecurity students, developers, and DevSecOps engineers who want to see exactly how SQL injection works at the code level and practice stopping it.

The lab provides three things:

1. **A deliberately vulnerable web application** (`app.py`) that accepts user input and inserts it directly into a SQL query using an f-string — the most common root cause of SQL injection in Python code.
2. **An automated audit script** (`audit_suite.py`) that fires real injection payloads at the application and shows you the raw database response, so you can see the damage each technique causes.
3. **A library of categorized payloads** (`payloads/`) covering every major injection class, with inline comments explaining how each one works.

The goal is not just to run attacks — it is to understand **why** each payload works, **what** the database sees when it executes, and **how** to write code that is immune to all of them.

> **Disclaimer**: This lab is for authorized security testing and education only. Deploy it only on systems you own. Never expose it to untrusted networks. Unauthorized access to computer systems is illegal.

---

## Repository Structure

```
.
├── app.py                # Vulnerable Flask server (binds to 0.0.0.0:5000)
├── init_lab.py           # Creates staging.db with 5 dummy accounts
├── audit_suite.py        # Automated injection tester (3 test cases)
├── requirements.txt      # Python dependencies (flask, requests)
├── payloads/             # Payload library organized by technique
│   ├── auth-bypass.txt
│   ├── union-based.txt
│   ├── blind-boolean.txt
│   ├── blind-time.txt
│   ├── error-based.txt
│   └── stacked-queries.txt
├── vulnerable-app/       # Extended multi-endpoint vulnerable app
│   ├── app.py
│   ├── setup_db.py
│   └── requirements.txt
├── scripts/              # Batch scanner and HTML report generator
│   ├── sqli_tester.py
│   └── report.py
└── docs/
    ├── deployment-guide.md   # Full Ubuntu/Debian deployment walkthrough
    └── prevention.md         # Parameterized query guide for 6 languages
```

---

## Setup Instructions

### Prerequisites

- Linux (Ubuntu/Debian recommended)
- Python 3.8+
- `pip` and `venv`

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd injection

python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs Flask (web server) and Requests (used by the audit script).

### 3. Initialize the database

```bash
python init_lab.py
```

This creates `staging.db` with an `accounts` table containing 5 dummy records:

| id | username   | password      | secret\_data                    |
|----|------------|---------------|---------------------------------|
| 1  | admin      | admin123      | FLAG{admin\_secret\_2024}       |
| 2  | jdoe       | p@ssw0rd!     | SSN: 123-45-6789                |
| 3  | alice      | alice.secret  | API\_KEY=sk-live-abc123xyz      |
| 4  | bob        | b0bBuilds!    | DB\_CONN=postgres://prod:...    |
| 5  | svc\_deploy | deploy#Token9 | AWS\_SECRET=wJalrXUtnFEMI/...   |

### 4. Start the vulnerable server

```bash
python app.py
```

The server starts on `http://0.0.0.0:5000`. The vulnerable endpoint is:

```
GET /api/search?id=<value>
```

The query it executes internally is:

```python
query = f"SELECT id, username, password, secret_data FROM accounts WHERE id = {user_id}"
```

No sanitization. No parameterization. The `id` value goes straight into the SQL string.

### 5. Run the audit suite

Open a second terminal (keep the server running):

```bash
source venv/bin/activate
python audit_suite.py
```

For a full Ubuntu/Debian deployment walkthrough (system updates, pip install, `nohup`/`screen` background execution, firewall rules), see [docs/deployment-guide.md](docs/deployment-guide.md).

---

## Injection Reference

The audit suite (`audit_suite.py`) tests three payloads against `/api/search?id=`. The table below explains exactly what each one does and why it works.

### Vulnerable code under test

```python
# app.py line 68 — the f-string that makes all of this possible
query = f"SELECT id, username, password, secret_data FROM accounts WHERE id = {user_id}"
```

### Payloads

| # | Type | Payload | What the database executes | How it works |
|---|------|---------|---------------------------|--------------|
| 1 | **Auth Bypass** | `1 OR '1'='1'` | `...WHERE id = 1 OR '1'='1'` | The `OR` introduces a second condition that is always true. Since `'1'` always equals `'1'`, the `WHERE` clause matches every row in the table. All 5 accounts are returned — usernames, passwords, and secrets. This is the classic tautology attack. |
| 2 | **Union-Based** (column count) | `1 ORDER BY 4--` | `...WHERE id = 1 ORDER BY 4--` | `ORDER BY 4` tells the database to sort results by the 4th column. If the query succeeds, the table has at least 4 columns. If it errors, it has fewer. Attackers increment this number (1, 2, 3, 4, 5...) until an error reveals the exact column count. The `--` characters **comment out** the rest of the original query so any trailing SQL from the application is ignored. |
| 3 | **Database Fingerprinting** | `0 UNION SELECT 1,sqlite_version(),3,4--` | `...WHERE id = 0 UNION SELECT 1,sqlite_version(),3,4--` | `WHERE id = 0` returns zero rows (no account has id 0). `UNION SELECT` appends a second result set crafted by the attacker. `sqlite_version()` is a built-in function that returns the database engine version (e.g., `3.45.1`). The `1,` `3,` and `4` are placeholder values that pad the result to match the 4 columns of the original query — a requirement for `UNION` to work. The `--` comments out everything after the injected SQL. Knowing the database engine lets an attacker select engine-specific exploits. |

### Key SQL injection building blocks

| Token | Purpose |
|-------|---------|
| `OR '1'='1'` | Always-true condition — forces the `WHERE` clause to match all rows |
| `ORDER BY N` | Probes column count — errors reveal the table structure |
| `UNION SELECT` | Appends attacker-controlled data to the original query's results |
| `--` | SQL line comment — **comments out** the rest of the query so injected syntax is valid |
| `sqlite_version()` | Built-in function — reveals the database engine and version to the attacker |
| `0` (as id) | Ensures the original query returns nothing, so only the `UNION` results are visible |

---

## Security Challenge

You have seen the payloads work. Now make them stop.

### Objective

Modify `app.py` so that **all three audit suite payloads fail** — the Auth Bypass returns only 1 row, the Union-Based probe cannot manipulate query structure, and the Database Fingerprinting payload returns an error or zero results.

### The rules

1. You may only edit `app.py`. Do not modify `audit_suite.py` or `init_lab.py`.
2. The endpoint `GET /api/search?id=1` must still return the correct account (normal functionality must be preserved).
3. You must not add a Web Application Firewall or blocklist of keywords. The fix must be at the query level.

### Hint — Parameterized queries

The vulnerable line is:

```python
# INSECURE — user input is concatenated directly into SQL
query = f"SELECT id, username, password, secret_data FROM accounts WHERE id = {user_id}"
rows = db.execute(query).fetchall()
```

Replace it with a **parameterized query** where `?` is a placeholder and the user input is passed as a separate argument. The database driver handles escaping — the input can never alter the query structure:

```python
# SECURE — user input is bound as a parameter, not concatenated
query = "SELECT id, username, password, secret_data FROM accounts WHERE id = ?"
rows = db.execute(query, (user_id,)).fetchall()
```

### Validation

After making your fix, restart the server and run the audit suite:

```bash
python app.py &
python audit_suite.py
```

**Expected results after a correct fix:**

| Test | Before (vulnerable) | After (patched) |
|------|-------------------|-----------------|
| Auth Bypass (`1 OR '1'='1'`) | 200 — all 5 rows returned | 500 error or 1 row only |
| Union-Based (`1 ORDER BY 4--`) | 200 — 1 row, query manipulated | 500 error — `--` treated as literal text |
| DB Fingerprinting (`0 UNION SELECT...`) | 200 — SQLite version leaked | 500 error — `UNION` treated as literal text |

When all three payloads are neutralized, you have successfully closed the SQL injection vulnerability.

### Going further

- Add input validation that rejects non-integer values for `id` before the query runs.
- Read [docs/prevention.md](docs/prevention.md) for parameterized query examples in Python, Node.js, Java, PHP, Go, and PostgreSQL.
- Try the extended lab in `vulnerable-app/` which has additional endpoints for blind injection and auth bypass practice.
- Run the full payload scanner: `python scripts/sqli_tester.py --target http://127.0.0.1:5000 --all`

---

## Additional Resources

- [docs/deployment-guide.md](docs/deployment-guide.md) — Full Ubuntu/Debian server deployment with `nohup` and `screen`
- [docs/prevention.md](docs/prevention.md) — Parameterized query guide for 6 languages + prevention checklist
- [payloads/](payloads/) — 6 payload files covering auth bypass, union, blind boolean, blind time, error-based, and stacked queries

## License

MIT — for educational and authorized testing use only.
