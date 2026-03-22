# SQL Injection Prevention Guide

## The Root Cause

SQL injection occurs when user input is concatenated directly into SQL queries:

```python
# VULNERABLE - never do this
query = f"SELECT * FROM users WHERE username='{user_input}'"
cursor.execute(query)
```

## Fix 1: Parameterized Queries (Best Practice)

Pass user input as parameters instead of concatenating into strings. The database driver handles escaping.

### Python (sqlite3)
```python
cursor.execute("SELECT * FROM users WHERE username=?", (user_input,))
```

### Python (psycopg2 / PostgreSQL)
```python
cursor.execute("SELECT * FROM users WHERE username=%s", (user_input,))
```

### Python (SQLAlchemy ORM)
```python
user = session.query(User).filter(User.username == user_input).first()
```

### Node.js (pg)
```javascript
const result = await pool.query(
  'SELECT * FROM users WHERE username=$1',
  [userInput]
);
```

### Java (PreparedStatement)
```java
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username=?"
);
stmt.setString(1, userInput);
ResultSet rs = stmt.executeQuery();
```

### PHP (PDO)
```php
$stmt = $pdo->prepare('SELECT * FROM users WHERE username = :username');
$stmt->execute(['username' => $userInput]);
```

### Go (database/sql)
```go
row := db.QueryRow("SELECT * FROM users WHERE username=$1", userInput)
```

## Fix 2: Input Validation

Validate and sanitize input before it reaches the query, as a defense-in-depth measure.

```python
import re

def validate_username(username):
    # Allow only alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]{1,50}$', username):
        raise ValueError("Invalid username")
    return username
```

For numeric IDs:
```python
def validate_id(user_id):
    return int(user_id)  # raises ValueError if not a number
```

## Fix 3: Least Privilege

Configure the database user with minimal permissions:

```sql
-- Create a read-only user for the web app
CREATE USER webapp WITH PASSWORD 'strong_password';
GRANT SELECT ON users, products TO webapp;
-- No INSERT, UPDATE, DELETE, DROP, or admin privileges
```

## Fix 4: Web Application Firewall (WAF) Rules

WAFs can catch common patterns, but should never be the only defense:

- Block requests containing `UNION SELECT`, `OR 1=1`, `--`, `/*`
- Rate-limit login attempts
- Log and alert on SQL error messages in responses

## Fix 5: Error Handling

Never expose database errors to users:

```python
try:
    result = db.execute(query)
except Exception:
    # Log the real error internally
    logger.exception("Database query failed")
    # Return a generic message to the user
    return {"error": "An internal error occurred"}, 500
```

## Fix 6: Stored Procedures (Defense in Depth)

```sql
CREATE PROCEDURE GetUser(IN p_username VARCHAR(50))
BEGIN
    SELECT id, username, role FROM users WHERE username = p_username;
END;
```

```python
cursor.callproc('GetUser', (user_input,))
```

## Checklist

- [ ] All SQL queries use parameterized statements
- [ ] No string concatenation or f-strings for SQL
- [ ] Input validation on all user-supplied values
- [ ] Database user has minimal required privileges
- [ ] Error messages don't expose SQL details to users
- [ ] WAF rules block common injection patterns
- [ ] Automated SQLi testing in CI/CD pipeline
- [ ] Regular security audits and code reviews
