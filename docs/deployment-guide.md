# Deployment Guide — Ubuntu / Debian Linux

Step-by-step instructions for deploying the SQL Injection Testing Lab on a fresh Ubuntu/Debian server.

> **Warning**: This lab is intentionally vulnerable. Deploy it only on an isolated machine or private network that you control. Never expose it to the public internet.

---

## Prerequisites

- Ubuntu 20.04+ or Debian 11+ (x86_64)
- A user account with `sudo` privileges
- Network access limited to authorized testers

---

## Step 1 — Update the System

Bring all packages up to date and install core utilities:

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2 — Install Python and pip

Install Python 3, pip, and the virtual-environment module:

```bash
sudo apt install -y python3 python3-pip python3-venv
```

Verify the installation:

```bash
python3 --version
pip3 --version
```

## Step 3 — Clone the Repository

```bash
git clone <your-repo-url> /opt/sqli-lab
cd /opt/sqli-lab
```

## Step 4 — Create a Virtual Environment

Isolate project dependencies from the system Python:

```bash
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now show `(venv)` to confirm the environment is active.

## Step 5 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask (web server) and Requests (audit script HTTP client).

## Step 6 — Initialize the Database

```bash
python init_lab.py
```

Expected output:

```
[+] Database created: /opt/sqli-lab/staging.db
[+] Table 'accounts' populated with 5 records
```

## Step 7 — Run the Application

### Option A — Run in the foreground (quick test)

```bash
python app.py
```

The server starts on `http://0.0.0.0:5000`. Press `Ctrl+C` to stop.

### Option B — Run in the background with `nohup`

`nohup` keeps the process running after you close the terminal. Output is written to `nohup.out`:

```bash
nohup python app.py > lab.log 2>&1 &
echo $!    # prints the PID for later reference
```

To stop it later:

```bash
# Find the process
ps aux | grep app.py

# Kill by PID
kill <PID>
```

### Option C — Run in the background with `screen`

`screen` gives you a detachable terminal session you can reattach to at any time:

```bash
# Install screen if not already present
sudo apt install -y screen

# Create a named session and start the app
screen -S sqli-lab
python app.py
```

Detach from the session (leave it running):

```
Ctrl+A then D
```

Reattach later:

```bash
screen -r sqli-lab
```

List all sessions:

```bash
screen -ls
```

Stop the app by reattaching and pressing `Ctrl+C`, or:

```bash
screen -X -S sqli-lab quit
```

## Step 8 — Verify the Deployment

From the server itself or any machine on the same network:

```bash
curl http://<server-ip>:5000/
curl http://<server-ip>:5000/api/search?id=1
```

Both should return JSON responses.

## Step 9 — Run the Audit Suite

With the server running, execute the test script:

```bash
# If using a virtual environment, make sure it is activated
source venv/bin/activate

python audit_suite.py --target http://127.0.0.1:5000
```

This runs all three injection test cases (Auth Bypass, Union-Based, Database Fingerprinting) and prints the results.

---

## Firewall Recommendations

Restrict access to port 5000 to only authorized testing IPs:

```bash
# Allow only your testing machine
sudo ufw allow from <tester-ip> to any port 5000

# Deny all other access to port 5000
sudo ufw deny 5000

# Enable the firewall
sudo ufw enable
```

## Teardown

When testing is complete, shut everything down and clean up:

```bash
# Stop the server (nohup method)
kill $(pgrep -f "python app.py")

# Stop the server (screen method)
screen -X -S sqli-lab quit

# Remove the database
rm -f staging.db

# Deactivate the virtual environment
deactivate

# Optional: remove the entire lab
rm -rf /opt/sqli-lab
```
