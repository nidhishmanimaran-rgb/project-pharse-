import sqlite3
import os
import shutil

BASE_DIR = os.path.dirname(__file__)
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "data")
FALLBACK_DATA_DIR = os.path.join("D:", "SQLi-playground-data")

storage_root = os.environ.get("SQLI_PLAYGROUND_ROOT")
if not storage_root:
    if os.path.exists(FALLBACK_DATA_DIR):
        try:
            free_bytes = shutil.disk_usage(BASE_DIR).free
        except OSError:
            free_bytes = 0
        if free_bytes < 10 * 1024 * 1024:
            storage_root = FALLBACK_DATA_DIR
        else:
            storage_root = DEFAULT_DATA_DIR
    else:
        storage_root = DEFAULT_DATA_DIR

os.makedirs(storage_root, exist_ok=True)
DB_PATH = os.path.join(storage_root, "users.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS users")
cur.execute("DROP TABLE IF EXISTS products")
cur.execute("DROP TABLE IF EXISTS orders")
cur.execute("DROP TABLE IF EXISTS feedback")
cur.execute("DROP TABLE IF EXISTS employees")
cur.execute("DROP TABLE IF EXISTS admin_credentials")
cur.execute("DROP TABLE IF EXISTS profiles")
cur.execute("DROP TABLE IF EXISTS admin_search")

cur.execute(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)"
)
cur.execute(
    "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, description TEXT)"
)
cur.execute(
    "CREATE TABLE feedback (id INTEGER PRIMARY KEY, user_id INTEGER, comment TEXT)"
)
cur.execute(
    "CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, quantity INTEGER, total REAL)"
)
cur.execute(
    "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, job TEXT, email TEXT)"
)
cur.execute(
    "CREATE TABLE profiles (id INTEGER PRIMARY KEY, username TEXT, fullname TEXT, email TEXT, role TEXT)"
)
cur.execute(
    "CREATE TABLE admin_credentials (id INTEGER PRIMARY KEY, admin_name TEXT, secret TEXT)"
)
cur.execute(
    "CREATE TABLE admin_search (id INTEGER PRIMARY KEY, admin_name TEXT, secret TEXT)"
)

cur.executemany(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    [
        ("alice", "alice123", "admin"),
        ("bob", "bobpass", "user"),
        ("charlie", "charliepwd", "auditor"),
        ("mallory", "mallorypw", "manager"),
    ],
)
cur.executemany(
    "INSERT INTO products (name, category, price, description) VALUES (?, ?, ?, ?)",
    [
        ("Laptop Pro", "electronics", 1299.99, "High-end laptop for professionals."),
        ("Gamer Mouse", "accessories", 59.99, "Precision mouse for gaming."),
        ("Office Chair", "furniture", 199.00, "Comfortable chair with lumbar support."),
        ("Coffee Mug", "kitchen", 12.50, "Ceramic mug for your morning coffee."),
    ],
)
cur.executemany(
    "INSERT INTO orders (user_id, product_id, quantity, total) VALUES (?, ?, ?, ?)",
    [
        (1, 1, 1, 1299.99),
        (2, 3, 2, 398.00),
        (3, 4, 3, 37.50),
    ],
)
cur.executemany(
    "INSERT INTO feedback (user_id, comment) VALUES (?, ?)",
    [
        (1, "Great product!"),
        (2, "Fast delivery."),
        (3, "Solid build quality."),
    ],
)
cur.executemany(
    "INSERT INTO employees (name, job, email) VALUES (?, ?, ?)",
    [
        ("Jane Doe", "Developer", "jane@example.com"),
        ("John Smith", "Support", "john@example.com"),
    ],
)
cur.executemany(
    "INSERT INTO profiles (username, fullname, email, role) VALUES (?, ?, ?, ?)",
    [
        ("alice", "Alice Admin", "alice@example.com", "admin"),
        ("bob", "Bob Builder", "bob@example.com", "user"),
        ("charlie", "Charlie Check", "charlie@example.com", "auditor"),
    ],
)
cur.executemany(
    "INSERT INTO admin_credentials (admin_name, secret) VALUES (?, ?)",
    [
        ("superadmin", "5f4dcc3b5aa765d61d8327deb882cf99"),
    ],
)
cur.executemany(
    "INSERT INTO admin_search (admin_name, secret) VALUES (?, ?)",
    [
        ("superadmin", "hidden_secret_value"),
    ],
)

conn.commit()
conn.close()
print(f"Created extended database at {DB_PATH}")
