from flask import Flask, request, render_template, g
import sqlite3
import os
import shutil

PROJECT_DIR = os.path.dirname(__file__)
DEFAULT_STORAGE = os.path.join(PROJECT_DIR, "data")
FALLBACK_STORAGE = os.path.join("D:", "SQLi-playground-data")

storage_root = os.environ.get("SQLI_PLAYGROUND_ROOT")
if not storage_root:
    if os.path.exists(FALLBACK_STORAGE):
        try:
            free_bytes = shutil.disk_usage(PROJECT_DIR).free
        except OSError:
            free_bytes = 0
        if free_bytes < 10 * 1024 * 1024:
            storage_root = FALLBACK_STORAGE
        else:
            storage_root = DEFAULT_STORAGE
    else:
        storage_root = DEFAULT_STORAGE

os.makedirs(storage_root, exist_ok=True)
DB_PATH = os.path.join(storage_root, "users.db")
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"


def get_db():
    db = getattr(g, "db", None)
    if db is None:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        g.db = db
    return db


@app.teardown_appcontext
def close_db(exception=None):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        db = get_db()
        sql = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            result = db.execute(sql).fetchone()
            if result:
                message = f"Welcome back, {result['username']}! Your role is {result['role']}"
            else:
                message = "Invalid login credentials. Try a different payload."
        except sqlite3.Error as err:
            message = f"Database error: {err}"
    return render_template("login.html", message=message)


@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    message = None
    query = ""
    executed_sql = ""
    if request.method == "POST":
        query = request.form.get("q", "")
        db = get_db()
        executed_sql = f"SELECT id, username, role FROM users WHERE username LIKE '%{query}%';"
        try:
            results = db.execute(executed_sql).fetchall()
            if not results:
                message = "No matching users found."
        except sqlite3.Error as err:
            message = f"Database error: {err}"
    return render_template("search.html", results=results, message=message, query=query, executed_sql=executed_sql)


@app.route("/search-safe", methods=["GET", "POST"])
def search_safe():
    results = []
    message = None
    query = ""
    executed_sql = ""
    if request.method == "POST":
        query = request.form.get("q", "")
        db = get_db()
        executed_sql = "SELECT id, username, role FROM users WHERE username LIKE ?;"
        try:
            results = db.execute(executed_sql, (f"%{query}%",)).fetchall()
            if not results:
                message = "No matching users found."
        except sqlite3.Error as err:
            message = f"Database error: {err}"
    return render_template("search.html", results=results, message=message, query=query, safe=True, executed_sql=executed_sql)


@app.route("/products", methods=["GET", "POST"])
def products():
    results = []
    message = None
    query = ""
    executed_sql = ""
    if request.method == "POST":
        query = request.form.get("q", "")
        db = get_db()
        executed_sql = f"SELECT id, name, category, price FROM products WHERE name LIKE '%{query}%';"
        try:
            results = db.execute(executed_sql).fetchall()
            if not results:
                message = "No matching products found."
        except sqlite3.Error as err:
            message = f"Database error: {err}"
    return render_template("products.html", results=results, message=message, query=query, executed_sql=executed_sql)


@app.route("/product", methods=["GET"])
def product_detail():
    product = None
    message = None
    executed_sql = ""
    product_id = request.args.get("id", "")
    if product_id:
        db = get_db()
        executed_sql = f"SELECT * FROM products WHERE id={product_id};"
        try:
            product = db.execute(executed_sql).fetchone()
            if not product:
                message = "No product found for that ID."
        except sqlite3.Error as err:
            message = f"Database error: {err}"
    return render_template("product_detail.html", product=product, message=message, executed_sql=executed_sql)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    profile = None
    message = None
    user = ""
    executed_sql = ""
    if request.method == "POST":
        user = request.form.get("user", "")
        db = get_db()
        executed_sql = f"SELECT username, fullname, email, role FROM profiles WHERE username = '{user}';"
        try:
            profile = db.execute(executed_sql).fetchone()
            if not profile:
                message = "No profile found."
        except sqlite3.Error as err:
            message = f"Database error: {err}"
    return render_template("profile.html", profile=profile, message=message, user=user, executed_sql=executed_sql)


@app.route("/admin-search", methods=["GET", "POST"])
def admin_search():
    results = []
    message = None
    query = ""
    executed_sql = ""
    if request.method == "POST":
        query = request.form.get("q", "")
        db = get_db()
        executed_sql = f"SELECT id, admin_name, secret FROM admin_search WHERE admin_name LIKE '%{query}%';"
        try:
            results = db.execute(executed_sql).fetchall()
            if not results:
                message = "No hidden admin results found."
        except sqlite3.Error as err:
            message = f"Database error: {err}"
    return render_template("admin_search.html", results=results, message=message, query=query, executed_sql=executed_sql)


@app.route("/challenges")
def challenges():
    flag = None
    if request.args.get("solved") == "true":
        flag = "SQLI-PLAYGROUND-LEVEL2-UNLOCKED"
    return render_template("challenge.html", flag=flag)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        print("Database not found. Run init_db_extended.py first.")
    app.run(debug=True)
