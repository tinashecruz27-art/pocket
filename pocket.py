import json


def load_expenses():
    try:
        with open("expenses.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_expenses(expenses):
    with open("expenses.json", "w") as file:
        json.dump(expenses, file, indent=2)


expenses = load_expenses()

while True:
    print()
    print("1) Add expense")
    print("2) View expenses")
    print("3) Quit")
    print("4) Total spent")
    choice = input("Choose: ")

    if choice == "1":
        amount = float(input("Amount: "))
        category = input("Category (food, transport...): ")
        note = input("Note: ")
        expense = {"amount": amount, "category": category, "note": note}
        expenses.append(expense)
        save_expenses(expenses)
        print("Saved!")

    elif choice == "2":
        for e in expenses:
            print(e["amount"], "-", e["category"], "-", e["note"])

    elif choice == "3":
        print("Bye!")
        break

    elif choice == "4":
        total = 0
        for e in expenses:
            total = total + e["amount"]
        print("Total:", total)

    else:
        print("Please choose 1, 2, 3 or 4")