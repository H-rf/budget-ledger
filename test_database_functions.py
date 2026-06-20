import pytest
import database_functions as db

@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    test_db = tmp_path/"test_budget.db"

    monkeypatch.setattr(db, "DB_NAME", str(test_db))

    db.create_transactions_table()

def test_add_transaction_returns_id_and_stores_cleaned_data():
    new_id = db.add_transaction("  Coffee  ", 10, " Expense ")

    assert new_id == 1
    assert db.get_transaction_by_id(new_id) == (1, "Coffee", 10.0, "expense")    

def test_update_rejects_invalid_amount_and_keeps_row():
    new_id = db.add_transaction("Groceries", 75, "expense")
    before = db.get_transaction_by_id(new_id)

    with pytest.raises(ValueError, match="amount must be a positive number"):
        db.update_transaction_by_id(new_id, -22)

    after = db.get_transaction_by_id(new_id)

    assert after == before

def test_delete_transaction_success():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 2

    affected = db.delete_transaction_by_id(salary_id)
    assert affected == 1
    assert db.get_transaction_by_id(salary_id) is None
    assert db.get_transaction_by_id(groceries_id) == (groceries_id, "Groceries", 75.0, "expense")

def test_delete_missing_transaction_returns_zero_and_keeps_existing_rows():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 2

    affected = db.delete_transaction_by_id(999)
    assert affected == 0

    assert db.get_transaction_by_id(salary_id) == (salary_id, "Salary", 1000.0, "income")
    assert db.get_transaction_by_id(groceries_id) == (groceries_id, "Groceries", 75.0, "expense")

def test_get_transactions_by_kind():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 2

    crypto_id = db.add_transaction("crypto", 40000, "income")
    assert crypto_id == 3

    clothes_id = db.add_transaction("clothes", 375, "expense")
    assert clothes_id == 4

    cars_id = db.add_transaction("cars", 10000, "expense")
    assert cars_id == 5

    transactions = db.get_transactions_by_kind("expense")
    assert transactions == [(groceries_id, "Groceries", 75.0, "expense"),(clothes_id, "clothes", 375.0, "expense"),(cars_id, "cars", 10000.0, "expense")]

    transactions = db.get_transactions_by_kind("income")
    assert transactions == [(salary_id, "Salary", 1000.0, "income"),(crypto_id, "crypto", 40000.0, "income")]

def test_get_missing_transactions_by_kind_returns_empty_list():
    transactions = db.get_transactions_by_kind("expense")
    assert transactions == []

def test_get_summary():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 2

    crypto_id = db.add_transaction("crypto", 40000, "income")
    assert crypto_id == 3

    clothes_id = db.add_transaction("clothes", 375, "expense")
    assert clothes_id == 4

    cars_id = db.add_transaction("cars", 10000, "expense")
    assert cars_id == 5

    summary = db.get_summary()
    assert summary == {
            "income": 41000.0,
            "expense": 10450.0,
            "balance": 30550.0
           } 

def test_get_summary_missing_transactions():
    summary = db.get_summary()
    assert summary == {
            "income": 0.0,
            "expense": 0.0,
            "balance": 0.0
           } 

def test_get_balance():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 2

    crypto_id = db.add_transaction("crypto", 40000, "income")
    assert crypto_id == 3

    clothes_id = db.add_transaction("clothes", 375, "expense")
    assert clothes_id == 4

    cars_id = db.add_transaction("cars", 10000, "expense")
    assert cars_id == 5

    balance = db.get_balance()
    assert balance == 30550.0

def test_get_balance_missing_transactions():
    balance = db.get_balance()
    assert balance == 0.0

def test_invalid_description_add_transaction():   
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    with pytest.raises(ValueError, match="description must be a non-empty string"):
        db.add_transaction("", 75, "expense")
    with pytest.raises(ValueError, match="description must be a non-empty string"):    
        db.add_transaction(99, 75, "expense")
    
    transactions = db.get_all_transactions()
    assert transactions == [(salary_id, "Salary", 1000.0, "income")]

def test_invalid_amount_add_transaction():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    with pytest.raises(ValueError, match="amount must be a positive number"):
        db.add_transaction("groceries", -99, "expense")
    with pytest.raises(ValueError, match="amount must be a positive number"):    
        db.add_transaction("groceries", True, "expense")
    with pytest.raises(ValueError, match="amount must be a positive number"):    
        db.add_transaction("groceries", 'twenty', "expense")
    with pytest.raises(ValueError, match="amount must be a positive number"):    
        db.add_transaction("groceries", "-99", "expense")

    transactions = db.get_all_transactions()
    assert transactions == [(salary_id, "Salary", 1000.0, "income")]   

def test_invalid_kind_add_transaction():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    with pytest.raises(ValueError, match="kind must be 'income' or 'expense'"):
        db.add_transaction("groceries", 454, 'food')

    transactions = db.get_all_transactions()
    assert transactions == [(salary_id, "Salary", 1000.0, "income")]     

def test_get_transaction_by_id_invalid_transaction_id():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    with pytest.raises(ValueError, match="transaction_id must be a positive integer"):
        db.get_transaction_by_id(-1)
    with pytest.raises(ValueError, match="transaction_id must be a positive integer"):    
        db.get_transaction_by_id(0)

    transactions = db.get_all_transactions()
    assert transactions == [(salary_id, "Salary", 1000.0, "income")] 

def test_update_transaction_by_id_rejects_invalid_id_and_keeps_existing_row():
    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 1
    
    before = db.get_transaction_by_id(groceries_id)

    
    with pytest.raises(ValueError, match="transaction_id must be a positive integer"):
        db.update_transaction_by_id(0, 50)

    with pytest.raises(ValueError, match="transaction_id must be a positive integer"):
        db.update_transaction_by_id(-99, 50)

    after = db.get_transaction_by_id(groceries_id)

    assert after == before

def test_delete_transaction_by_id_rejects_invalid_id_and_keeps_existing_row():
    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 1
   
    before = db.get_transaction_by_id(groceries_id)

    
    with pytest.raises(ValueError, match="transaction_id must be a positive integer"):
        db.delete_transaction_by_id(0)

    with pytest.raises(ValueError, match="transaction_id must be a positive integer"):
        db.delete_transaction_by_id(-99)

    after = db.get_transaction_by_id(groceries_id)

    assert after == before

def test_get_transaction_by_id_existing_and_missing():
    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 1

    assert db.get_transaction_by_id(groceries_id) == (groceries_id, "Groceries", 75.0, "expense")
    assert db.get_transaction_by_id(999) is None

def test_update_transaction_by_id_success():
    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 1

    affected_row = db.update_transaction_by_id(groceries_id, 90)
    assert affected_row == 1

    assert db.get_transaction_by_id(groceries_id) == (groceries_id, "Groceries", 90.0, "expense")

def test_update_transaction_by_id_missing_id_returns_zero():
    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 1

    before = db.get_transaction_by_id(groceries_id)

    affected_row = db.update_transaction_by_id(999, 90)
    assert affected_row == 0

    after = db.get_transaction_by_id(groceries_id)

    assert before == after

def test_delete_transaction_by_id_missing_id_returns_zero():
    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 1

    before = db.get_transaction_by_id(groceries_id)

    affected_row = db.delete_transaction_by_id(999)
    assert affected_row == 0

    after = db.get_transaction_by_id(groceries_id)

    assert before == after

def test_get_transactions_by_kind_rejects_invalid_kind():
    with pytest.raises(ValueError, match="kind must be 'income' or 'expense'"):
        db.get_transactions_by_kind("food")

def test_get_transactions_by_kind_normalizes_kind():
    salary_id = db.add_transaction("Salary", 1000, "income")
    assert salary_id == 1

    groceries_id = db.add_transaction("Groceries", 75, "expense")
    assert groceries_id == 2

    expense_transaction = db.get_transactions_by_kind(" Expense ")
    assert expense_transaction == [(groceries_id, "Groceries", 75.0, "expense")]

def test_get_full_summary_with_income_and_expense():
    db.add_transaction("Salary", 4000, "income")
    db.add_transaction("groceries", 300, "expense")

    assert db.get_full_summary() == {
        "count": 2,
        "income_count": 1,
        "expense_count": 1,
        "total_income": 4000.0,
        "total_expense": 300.0,
        "balance": 3700.0
    }    







    




    










    





