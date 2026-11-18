import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
DATABASE = "pocket.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    selected = request.args.get("category", "")
    conn = get_db()

    if selected:
        expenses = conn.execute("""
            SELECT id, amount, category, note,
                   datetime(created_at, 'localtime') AS created_at
            FROM expenses
            WHERE category = ?
            ORDER BY id DESC
        """, (selected,)).fetchall()
        total = conn.execute(
            "SELECT SUM(amount) FROM expenses WHERE category = ?", (selected,)
        ).fetchone()[0] or 0
    else:
        expenses = conn.execute("""
            SELECT id, amount, category, note,
                   datetime(created_at, 'localtime') AS created_at
            FROM expenses
            ORDER BY id DESC
        """).fetchall()
        total = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0

    by_category = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    by_month = conn.execute("""
        SELECT strftime('%Y-%m', created_at, 'localtime') AS month,
               SUM(amount) AS total
        FROM expenses
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()

    conn.close()
    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        by_category=by_category,
        by_month=by_month,
        selected=selected,
    )


@app.route("/add", methods=["POST"])
def add():
    amount = float(request.form["amount"])
    category = request.form["category"].lower()
    note = request.form["note"]

    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (amount, category, note) VALUES (?, ?, ?)",
        (amount, category, note),
    )
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)