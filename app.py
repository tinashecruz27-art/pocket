import json
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


def load_expenses():
    try:
        with open("expenses.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_expenses(expenses):
    with open("expenses.json", "w") as file:
        json.dump(expenses, file, indent=2)


@app.route("/")
def home():
    expenses = load_expenses()
    total = 0
    for e in expenses:
        total = total + e["amount"]
    return render_template("index.html", expenses=expenses, total=total)


@app.route("/add", methods=["POST"])
def add():
    amount = float(request.form["amount"])
    category = request.form["category"].lower()
    note = request.form["note"]

    expenses = load_expenses()
    expenses.append({"amount": amount, "category": category, "note": note})
    save_expenses(expenses)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)