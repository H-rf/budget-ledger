import sqlite3

DB_NAME = "budget.db"


def create_transactions_table():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        description TEXT,
        amount REAL,
        kind TEXT
    )
    """)

    connection.commit()
    connection.close()

#create_transactions_table()

def validate_transaction_id(transaction_id):
    if not isinstance(transaction_id,int) or isinstance(transaction_id,bool) or transaction_id<=0:
        raise ValueError("transaction_id must be a positive integer")


def validate_description(description):
    if not isinstance(description, str) or description.strip() == "":
        raise ValueError("description must be a non-empty string")

    description = description.strip()
    return description


def validate_amount(amount):
    if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("amount must be a positive number")


def validate_kind(kind):
    if not isinstance(kind, str):
        raise ValueError("kind must be 'income' or 'expense'")

    kind = kind.strip().lower()

    if kind not in ("income", "expense"):
        raise ValueError("kind must be 'income' or 'expense'")
    
    return kind


def add_transaction(description, amount, kind):
    description = validate_description(description)
    validate_amount(amount)
    kind = validate_kind(kind)
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO transactions(description, amount, kind)
    VALUES(?, ?, ?)
    """, (description, amount, kind))

    new_id = cursor.lastrowid

    connection.commit()
    connection.close()
    return new_id

#create_transactions_table()
#add_transaction("Bonus", 500, "income")  

def get_all_transactions():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY id")
   
    rows = cursor.fetchall()
    
    
    connection.close()
    return rows

#transactions = get_all_transactions()
#print(transactions)  


def get_transactions_by_kind(kind):
    kind = validate_kind(kind)
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM transactions WHERE kind = ? ORDER BY id",
    (kind,)
    )
    rows=cursor.fetchall()
    connection.close()
    return rows

#transactions = get_transactions_by_kind("food")
#print(transactions)    


def get_transaction_by_id(transaction_id):
    validate_transaction_id(transaction_id)
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM transactions WHERE id = ?",
    (transaction_id,)
    )
    row = cursor.fetchone()
    connection.close()
    return row

#transaction = get_transaction_by_id(999)
#print(transaction)

def update_transaction_by_id(transaction_id, new_amount):
    validate_transaction_id(transaction_id)
    validate_amount(new_amount)
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("UPDATE transactions SET amount = ? WHERE id = ?",(new_amount, transaction_id))
    affected_rows = cursor.rowcount
    connection.commit()
    connection.close()   
    return affected_rows

#affected = update_transaction_by_id(999, 75)
#print(affected)

#transaction = get_transaction_by_id(999)
#print(transaction)

def delete_transaction_by_id(transaction_id):
    validate_transaction_id(transaction_id)
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM transactions WHERE id = ?",(transaction_id,))
    affected_rows = cursor.rowcount
    connection.commit()
    connection.close()
    return affected_rows

#affected = delete_transaction_by_id(6)
#print(affected)

#transaction = get_transaction_by_id(6)
#print(transaction)

#transactions = get_all_transactions()
#print(transactions)

#affected = delete_transaction_by_id(999)
#print(affected)

def get_balance():
    transactions = get_all_transactions()

    balance = 0

    for transaction in transactions:

        amount = transaction[2]
        kind = transaction[3]

        if kind == "income" :
            balance += amount
        elif kind == "expense" :
            balance -= amount

    return balance

#balance = get_balance()
#print(balance)  

def get_summary():
    transactions = get_all_transactions()

    total_income = 0
    total_expense = 0

    for transaction in transactions:
        amount = transaction[2]
        kind = transaction[3]

        if kind == "income":
            total_income += amount
        elif kind == "expense":
            total_expense += amount

    balance = total_income - total_expense

    return {
            "income": total_income,
            "expense": total_expense,
            "balance": balance
           } 

def get_full_summary():
    transactions = get_all_transactions()
    count = len(transactions)
    income_count = 0
    expense_count = 0
    total_income = 0
    total_expense = 0

    for transaction in transactions:
        amount = transaction[2]
        kind = transaction[3]

        if kind == "income":
            income_count += 1
            total_income += amount
        elif kind == "expense":
            expense_count += 1
            total_expense += amount

    balance = total_income - total_expense

    return {
        "count": count,
        "income_count": income_count,
        "expense_count": expense_count,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }

if __name__ == "__main__":
    before = get_transaction_by_id(5)
    print("before:", before)

    try:
        update_transaction_by_id(5, -999)
    except ValueError as error:
        print("error:", error)

    after = get_transaction_by_id(5)
    print("after:", after)

    print("same:", before == after)




        










