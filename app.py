import os
import sqlite3
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "pocket.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER REFERENCES users(id)
        )
    """)

    # Older databases don't have the user_id column yet, so add it
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(expenses)")]
    if "user_id" not in columns:
        conn.execute("ALTER TABLE expenses ADD COLUMN user_id INTEGER REFERENCES users(id)")

    conn.commit()
    conn.close()


# Create the tables as soon as the app is loaded (works locally AND on a server)
init_db()


# ---------- Accounts ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]

        if len(username) < 3:
            return render_template("register.html", error="Username must be at least 3 characters.")
        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters.")

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            conn.close()
            return render_template("register.html", error="That username is already taken.")

        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        user_id = cursor.lastrowid

        # The very first user to sign up gets the expenses created before accounts existed
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 1:
            conn.execute("UPDATE expenses SET user_id = ? WHERE user_id IS NULL", (user_id,))

        conn.commit()
        conn.close()

        session.clear()
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Wrong username or password.")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- Expenses ----------

@app.route("/")
def home():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    selected = request.args.get("category", "")
    conn = get_db()

    if selected:
        expenses = conn.execute("""
            SELECT id, amount, category, note,
                   datetime(created_at, 'localtime') AS created_at
            FROM expenses
            WHERE user_id = ? AND category = ?
            ORDER BY id DESC
        """, (user_id, selected)).fetchall()
        total = conn.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id = ? AND category = ?",
            (user_id, selected),
        ).fetchone()[0] or 0
    else:
        expenses = conn.execute("""
            SELECT id, amount, category, note,
                   datetime(created_at, 'localtime') AS created_at
            FROM expenses
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()
        total = conn.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,)
        ).fetchone()[0] or 0

    by_category = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
    """, (user_id,)).fetchall()

    by_month = conn.execute("""
        SELECT strftime('%Y-%m', created_at, 'localtime') AS month,
               SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month DESC
    """, (user_id,)).fetchall()

    conn.close()

    chart_labels = [c["category"] for c in by_category]
    chart_values = [c["total"] for c in by_category]

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        by_category=by_category,
        by_month=by_month,
        selected=selected,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


@app.route("/add", methods=["POST"])
def add():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    amount = float(request.form["amount"])
    category = request.form["category"].lower()
    note = request.form["note"]

    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (amount, category, note, user_id) VALUES (?, ?, ?, ?)",
        (amount, category, note, user_id),
    )
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)