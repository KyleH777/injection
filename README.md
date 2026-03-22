# SQL Injection Security Testing Hub

A collection of SQL injection payloads, a purposely vulnerable test application, and automated testing scripts for **authorized security testing and education**.

> **Disclaimer**: Use these tools only on systems you own or have explicit written authorization to test. Unauthorized access to computer systems is illegal.

## Structure

```
.
├── app.py                # Vulnerable Flask app (0.0.0.0:5000)
├── init_lab.py           # Database initializer (creates staging.db)
├── audit_suite.py        # Automated injection test runner
├── requirements.txt      # Python dependencies
├── payloads/             # Categorized SQL injection payloads
│   ├── auth-bypass.txt
│   ├── union-based.txt
│   ├── blind-boolean.txt
│   ├── blind-time.txt
│   ├── error-based.txt
│   └── stacked-queries.txt
├── vulnerable-app/       # Extended vulnerable Flask app (multi-endpoint)
│   ├── app.py
│   ├── setup_db.py
│   └── requirements.txt
├── scripts/              # Automated testing scripts
│   ├── sqli_tester.py
│   └── report.py
└── docs/                 # Guides & references
    ├── prevention.md
    └── deployment-guide.md
```

## Quick Start

### 1. Set up the vulnerable test app

```bash
cd vulnerable-app
pip install -r requirements.txt
python setup_db.py
python app.py
```

The app runs at `http://127.0.0.1:5000` with these endpoints:

| Endpoint | Method | Parameter | Vulnerability |
|---|---|---|---|
| `/login` | POST | `username`, `password` | Auth bypass |
| `/search` | GET | `q` | Union-based, error-based |
| `/user` | GET | `id` | Blind boolean, time-based |

### 2. Run the automated tester

```bash
cd scripts
python sqli_tester.py --target http://127.0.0.1:5000
```

### 3. Browse payloads

Each file in `payloads/` contains ready-to-use injection strings organized by technique, with comments explaining how they work.

## Payload Categories

| Category | File | Use Case |
|---|---|---|
| Auth Bypass | `auth-bypass.txt` | Bypass login forms |
| Union-Based | `union-based.txt` | Extract data via UNION SELECT |
| Blind (Boolean) | `blind-boolean.txt` | Infer data from true/false responses |
| Blind (Time) | `blind-time.txt` | Infer data from response delays |
| Error-Based | `error-based.txt` | Extract data from error messages |
| Stacked Queries | `stacked-queries.txt` | Execute multiple statements |

## Deployment

See [docs/deployment-guide.md](docs/deployment-guide.md) for full Ubuntu/Debian setup instructions covering system updates, Python installation, virtual environments, dependency installation, and running the app in the background with `nohup` or `screen`.

## License

MIT - for educational and authorized testing use only.
