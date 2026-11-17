import json
from app import get_db, init_db

init_db()

with open("expenses.json", "r") as file:
    old_expenses = json.load(file)

conn = get_db()
for e in old_expenses:
    conn.execute(
        "INSERT INTO expenses (amount, category, note) VALUES (?, ?, ?)",
        (e["amount"], e["category"].lower(), e["note"]),
    )
conn.commit()
conn.close()

print("Moved", len(old_expenses), "expenses into the database")