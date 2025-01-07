import sqlite3
from getpass import getpass
import datetime

# Database setup
def init_db():
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
    print("Database initialized.")

# User registration and authentication
def register_user():
    username = input("Enter a username: ")
    password = getpass("Enter a password: ")
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            print("User registered successfully!")
        except sqlite3.IntegrityError:
            print("Username already exists. Please try another.")

def login_user():
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            print("Login successful!")
            return user[0]  # Return user ID
        else:
            print("Invalid credentials.")
            return None

# Income and expense tracking
def add_transaction(user_id):
    type = input("Enter transaction type (income/expense): ").lower()
    category = input("Enter category : ")
    amount = float(input("Enter amount: "))
    date = input("Enter date (YYYY-MM-DD): ") or str(datetime.date.today())
    month = date[:7]  # Extract the year and month (YYYY-MM)

    if type == "expense":
        with sqlite3.connect("finance_manager.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT b.amount, COALESCE(SUM(t.amount), 0) AS spent
                FROM budgets b
                LEFT JOIN transactions t 
                ON b.user_id = t.user_id AND b.category = t.category 
                AND t.type = 'expense' AND strftime('%Y-%m', t.date) = b.month
                WHERE b.user_id = ? AND b.category = ? AND b.month = ?
                GROUP BY b.category
                """,
                (user_id, category, month),
            )
            budget = cursor.fetchone()
            if budget:
                budget_amount, spent = budget
                if spent + amount > budget_amount:
                    print(f"--> ALERT: Adding this transaction exceeds your budget for {category} this month!")
                    return

    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, type, category, amount, date),
        )
        conn.commit()
        print("Transaction added successfully.")


# View transactions
def view_transactions(user_id):
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, category, amount, date FROM transactions WHERE user_id = ?", (user_id,))
        transactions = cursor.fetchall()
        print("\nTransactions:")
        for t in transactions:
            print(f"ID: {t[0]} | {t[4]} | {t[1].capitalize()} | {t[2]} | ${t[3]:.2f}")

def update_transaction(user_id):
    view_transactions(user_id)
    transaction_id = int(input("Enter the ID of the transaction to update: "))
    type = input("Enter new transaction type (income/expense): ").lower()
    category = input("Enter new category: ")
    amount = float(input("Enter new amount: "))
    date = input("Enter new date (YYYY-MM-DD): ") or str(datetime.date.today())
    month = date[:7]  # Extract the year and month (YYYY-MM)

    if type == "expense":
        with sqlite3.connect("finance_manager.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT b.amount, COALESCE(SUM(t.amount), 0) AS spent
                FROM budgets b
                LEFT JOIN transactions t 
                ON b.user_id = t.user_id AND b.category = t.category 
                AND t.type = 'expense' AND strftime('%Y-%m', t.date) = b.month
                WHERE b.user_id = ? AND b.category = ? AND b.month = ?
                GROUP BY b.category
                """,
                (user_id, category, month),
            )
            budget = cursor.fetchone()
            if budget:
                budget_amount, spent = budget
                cursor.execute(
                    "SELECT amount FROM transactions WHERE id = ? AND user_id = ?",
                    (transaction_id, user_id),
                )
                current_amount = cursor.fetchone()[0]
                spent -= current_amount  # Subtract current transaction amount from spent
                if spent + amount > budget_amount:
                    print(f"--> ALERT: Updating this transaction exceeds your budget for {category} this month!")
                    return

    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE transactions
            SET type = ?, category = ?, amount = ?, date = ?
            WHERE id = ? AND user_id = ?
            """,
            (type, category, amount, date, transaction_id, user_id),
        )
        conn.commit()
        print("Transaction updated successfully.")
def view_transactions(user_id):
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, category, amount, date FROM transactions WHERE user_id = ?", (user_id,))
        transactions = cursor.fetchall()
        print("\nTransactions:")
        for t in transactions:
            print(f"ID: {t[0]} | {t[4]} | {t[1].capitalize()} | {t[2]} | ${t[3]:.2f}")


def delete_transaction(user_id):
    view_transactions(user_id)
    transaction_id = int(input("Enter the ID of the transaction to delete: "))
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
        conn.commit()
        print("Transaction deleted successfully.")



# Financial reports
def generate_report(user_id):
    print("\n1. Monthly Report\n2. Yearly Report")
    choice = input("Choose an option: ")

    if choice == "1":
        year = input("Enter year (YYYY): ")
        month = input("Enter month (MM): ")
        start_date = f"{year}-{month}-01"
        end_date = f"{year}-{month}-31"
    elif choice == "2":
        year = input("Enter year (YYYY): ")
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
    else:
        print("Invalid choice.")
        return

    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expense
            FROM transactions
            WHERE user_id = ? AND date BETWEEN ? AND ?
            """,
            (user_id, start_date, end_date),
        )
        result = cursor.fetchone()
        total_income = result[0] or 0
        total_expense = result[1] or 0
        print(f"\nFinancial Report ({'Monthly' if choice == '1' else 'Yearly'}):\nTotal Income: ${total_income:.2f}\nTotal Expense: ${total_expense:.2f}\nSavings: ${total_income - total_expense:.2f}")



# Budgeting
def set_budget(user_id):
    category = input("Enter category: ")
    amount = float(input("Enter budget amount: "))
    month = input("Enter month (YYYY-MM): ")
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO budgets (user_id, category, month, amount) VALUES (?, ?, ?, ?)",
            (user_id, category, month, amount),
        )
        conn.commit()
        print("Monthly budget set successfully.")

def check_budget(user_id):
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.category, b.amount, COALESCE(SUM(t.amount), 0) AS spent, b.month
            FROM budgets b
            LEFT JOIN transactions t 
            ON b.user_id = t.user_id AND b.category = t.category 
            AND t.type = 'expense' AND strftime('%Y-%m', t.date) = b.month
            WHERE b.user_id = ?
            GROUP BY b.category, b.month
        """, (user_id,))
        budgets = cursor.fetchall()
        print("\nBudget Report:")
        for b in budgets:
            print(f"Category: {b[0]} | Budget: ${b[1]:.2f} | Spent: ${b[2]:.2f} | Month: {b[3]}")
            if b[2] > b[1]:
                print(f"--> ALERT: You have exceeded your budget for {b[0]} in {b[3]}!")


# Main program loop
def main():
    init_db()
    print("Welcome to the Personal Finance Management Application!")
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            register_user()
        elif choice == "2":
            user_id = login_user()
            if user_id:
                while True:
                    print("\n1. Add Transaction\n2. View Transactions\n3. Update Transaction\n4. Delete Transaction\n5. Generate Report\n6. Set Budget\n7. Check Budget\n8. Logout")
                    sub_choice = input("Choose an option: ")
                    if sub_choice == "1":
                        add_transaction(user_id)
                    elif sub_choice == "2":
                        view_transactions(user_id)
                    elif sub_choice == "3":
                        update_transaction(user_id)
                    elif sub_choice == "4":
                        delete_transaction(user_id)
                    elif sub_choice == "5":
                        generate_report(user_id)
                    elif sub_choice == "6":
                        set_budget(user_id)
                    elif sub_choice == "7":
                        check_budget(user_id)
                    elif sub_choice == "8":
                        break
                    else:
                        print("Invalid choice. Try again.")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
