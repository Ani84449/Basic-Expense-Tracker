import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date


def connect_database():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    """)

    connection.commit()
    connection.close()


def add_transaction():
    transaction_type = type_box.get()
    category = category_entry.get()
    amount = amount_entry.get()
    description = description_entry.get()
    current_date = date.today().strftime("%d/%m/%Y")

    if category == "" or amount == "":
        messagebox.showerror("Error", "Please enter category and amount.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")
        return

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions (date, type, category, amount, description)
        VALUES (?, ?, ?, ?, ?)
    """, (current_date, transaction_type, category, amount, description))

    connection.commit()
    connection.close()

    clear_entries()
    load_transactions()
    update_summary()

    messagebox.showinfo("Success", "Transaction added successfully.")


def load_transactions():
    for row in transaction_table.get_children():
        transaction_table.delete(row)

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, date, type, category, amount, description
        FROM transactions
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    connection.close()

    for record in records:
        transaction_table.insert(
            "",
            "end",
            iid=record[0],
            values=(
                record[1],
                record[2],
                record[3],
                f"£{record[4]:.2f}",
                record[5]
            )
        )


def update_summary():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Income'")
    total_income = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Expense'")
    total_expenses = cursor.fetchone()[0]

    connection.close()

    if total_income is None:
        total_income = 0

    if total_expenses is None:
        total_expenses = 0

    balance = total_income - total_expenses

    income_label.config(text=f"Total Income: £{total_income:.2f}")
    expenses_label.config(text=f"Total Expenses: £{total_expenses:.2f}")
    balance_label.config(text=f"Current Balance: £{balance:.2f}")


def delete_transaction():
    selected_item = transaction_table.selection()

    if not selected_item:
        messagebox.showerror("Error", "Please select a transaction to delete.")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this transaction?"
    )

    if confirm:
        transaction_id = selected_item[0]

        connection = sqlite3.connect("expenses.db")
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

        connection.commit()
        connection.close()

        load_transactions()
        update_summary()

        messagebox.showinfo("Deleted", "Transaction deleted successfully.")


def clear_entries():
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    type_box.set("Expense")


root = tk.Tk()
root.title("Basic Expense Tracker")
root.geometry("900x600")


title_label = tk.Label(
    root,
    text="Basic Expense Tracker",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=10)


main_frame = tk.Frame(root)
main_frame.pack(pady=10)


tk.Label(main_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5)

type_box = ttk.Combobox(
    main_frame,
    values=["Income", "Expense"],
    state="readonly"
)
type_box.grid(row=0, column=1, padx=5, pady=5)
type_box.set("Expense")


tk.Label(main_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)

category_entry = tk.Entry(main_frame)
category_entry.grid(row=1, column=1, padx=5, pady=5)


tk.Label(main_frame, text="Amount (£):").grid(row=2, column=0, padx=5, pady=5)

amount_entry = tk.Entry(main_frame)
amount_entry.grid(row=2, column=1, padx=5, pady=5)


tk.Label(main_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5)

description_entry = tk.Entry(main_frame)
description_entry.grid(row=3, column=1, padx=5, pady=5)


button_frame = tk.Frame(root)
button_frame.pack(pady=10)

add_button = tk.Button(
    button_frame,
    text="Add Transaction",
    width=18,
    command=add_transaction
)
add_button.grid(row=0, column=0, padx=5)

delete_button = tk.Button(
    button_frame,
    text="Delete Selected",
    width=18,
    command=delete_transaction
)
delete_button.grid(row=0, column=1, padx=5)

clear_button = tk.Button(
    button_frame,
    text="Clear Fields",
    width=18,
    command=clear_entries
)
clear_button.grid(row=0, column=2, padx=5)


summary_frame = tk.Frame(root)
summary_frame.pack(pady=10)

income_label = tk.Label(
    summary_frame,
    text="Total Income: £0.00",
    font=("Arial", 12, "bold")
)
income_label.grid(row=0, column=0, padx=15)

expenses_label = tk.Label(
    summary_frame,
    text="Total Expenses: £0.00",
    font=("Arial", 12, "bold")
)
expenses_label.grid(row=0, column=1, padx=15)

balance_label = tk.Label(
    summary_frame,
    text="Current Balance: £0.00",
    font=("Arial", 12, "bold")
)
balance_label.grid(row=0, column=2, padx=15)


columns = (
    "Date",
    "Type",
    "Category",
    "Amount",
    "Description"
)

transaction_table = ttk.Treeview(
    root,
    columns=columns,
    show="headings"
)

for column in columns:
    transaction_table.heading(column, text=column)
    transaction_table.column(column, width=160)

transaction_table.pack(
    pady=10,
    fill="both",
    expand=True
)


connect_database()
load_transactions()
update_summary()

root.mainloop()
