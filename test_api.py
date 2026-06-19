import pytest
from fastapi.testclient import TestClient

from main import app
import database_functions as db

client = TestClient(app)

def create_transaction(description="Salary", amount=1000, kind="income"):
    return client.post(
        "/transactions",
        json={
            "description": description,
            "amount": amount,
            "kind": kind
        }
    )

@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    test_db = tmp_path/"test_budget.db"

    monkeypatch.setattr(db, "DB_NAME", str(test_db))

    db.create_transactions_table()


def test_get_balance_initially_zero():
    response = client.get("/balance")

    assert response.status_code == 200
    assert response.json() == {
        "income": 0,
        "expense": 0,
        "balance": 0
    }


def test_create_transaction_success():
    response = client.post(
        "/transactions",
        json={
            "description": "Salary",
            "amount": 1000,
            "kind": "income"
        }
    )

    assert response.status_code == 201
    assert response.json() == {"status": "ok"}    


def test_created_transaction_appears_in_transactions_list():
    client.post(
        "/transactions",
        json={
            "description": "Salary",
            "amount": 1000,
            "kind": "income"
        }
    )

    response = client.get("/transactions")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "transactions": [
            {
                "description": "Salary",
                "amount": 1000,
                "kind": "income"
            }
        ]
    }    


def test_create_income_transaction_returns_201():
    response=client.post("/transactions",
    json={
  "description": "Salary",
  "amount": 1000,
  "kind": "income"
})

    assert response.status_code==201
    assert response.json() == {"status": "ok"}


def test_create_transaction_invalid_kind_returns_400():
    response=client.post("/transactions",
    json={
    "description": "Salary",
    "amount": 1000,
    "kind": "banana"
})
    
    assert response.status_code==400
    assert response.json()=={"detail": "Invalid transaction data"}

def test_created_transaction_appears_in_transactions_list():
    create_response=client.post("/transactions",
    json={
  "description": "Salary",
  "amount": 1000,
  "kind": "income"
})
    assert create_response.status_code == 201
    response=client.get("/transactions")
    assert response.status_code == 200
    assert response.json()=={
    "status": "ok",
    "transactions": [
        {
            "description": "Salary",
            "amount": 1000,
            "kind": "income"
        }
    ]
}

def test_find_existing_transaction_by_description():
    create_response=client.post("/transactions",
    json={
  "description": "Salary",
  "amount": 1000,
  "kind": "income"
})
    assert create_response.status_code==201
    response=client.get("/transactions/Salary")
    assert response.status_code==200
    assert response.json()=={
    "status": "ok",
    "transaction": {
        "description": "Salary",
        "amount": 1000,
        "kind": "income"
    }
}

def test_find_missing_transaction_returns_404():
    response = client.get("/transactions/DoesNotExist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Transaction not found"}

def test_delete_existing_transaction_removes_it():
    create_response = client.post(
        "/transactions",
        json={
            "description": "Salary",
            "amount": 1000,
            "kind": "income"
        }
    )

    assert create_response.status_code == 201

    delete_response = client.delete("/transactions/Salary")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"status": "ok"}

    find_response = client.get("/transactions/Salary")

    assert find_response.status_code == 404
    assert find_response.json() == {"detail": "Transaction not found"} 

def test_update_transaction_valid_new_amount():
    create_response=client.post(
        "/transactions",
        json={
            "description": "Salary",
            "amount": 1000,
            "kind": "income"
        }
    )

    assert create_response.status_code==201
    patch_response=client.patch("/transactions/Salary",
    json={
        "amount": 1200
    })
    assert patch_response.status_code==200
    find_response=client.get("/transactions/Salary")
    assert find_response.status_code==200
    assert find_response.json() == {
    "status": "ok",
    "transaction": {
        "description": "Salary",
        "amount": 1200,
        "kind": "income"
    }
}

def test_update_transaction_invalid_new_amount():
    create_response=client.post(
        "/transactions",
        json={
            "description": "Salary",
            "amount": 1000,
            "kind": "income"
        }
    )

    assert create_response.status_code==201
    patch_response=client.patch("/transactions/Salary",
    json={
        "amount": -112
    })
    assert patch_response.status_code==400
    find_response=client.get("/transactions/Salary")
    assert find_response.status_code==200
    assert find_response.json() == {
    "status": "ok",
    "transaction": {
            "description": "Salary",
            "amount": 1000,
            "kind": "income"
        }
}


def test_update_non_existing_transaction():
    patch_response=client.patch("/transactions/Salary",
    json={
        "amount": 1000
    })
    assert patch_response.status_code==404
    find_response=client.get("/transactions/Salary")
    assert find_response.status_code == 404
    assert find_response.json() == {"detail": "Transaction not found"}


def test_balance_updates_after_income_and_expense():
    create_response1=create_transaction()
    assert create_response1.status_code==201
    create_response2=create_transaction("Rent", 300, "expense")
    assert create_response2.status_code==201
    balance_response=client.get("/balance")
    assert balance_response.status_code==200
    assert balance_response.json()=={
                                  "income": 1000,
                                  "expense": 300,
                                  "balance": 700
                                }

def test_create_transaction_missing_amount_returns_422():
    response=client.post(
        "/transactions",
        json={
            "description": "Salary",
            "kind": "income"
        })    

    assert response.status_code==422


def test_create_transaction_invalid_amount_type_returns_422():
    response=client.post(
        "/transactions",
        json={
            "description": "Salary",
            "amount": "abc",
            "kind": "income"
         }
        )

    assert response.status_code==422    


def test_transaction_count_after_creating_transactions():
    response1 = create_transaction()
    assert response1.status_code == 201

    response2 = create_transaction("Rent", 300, "expense")
    assert response2.status_code == 201

    response = client.get("/transactions/count")

    assert response.status_code == 200
    assert response.json() == {"count": 2}

def test_get_transactions_filters_by_kind():
    response1 = create_transaction()
    assert response1.status_code == 201

    response2 = create_transaction("Shopping", 300, "expense")
    assert response2.status_code == 201

    expense_response = client.get("/transactions?kind=expense")

    assert expense_response.status_code == 200
    assert expense_response.json() == {
        "status": "ok",
        "transactions": [
            {
                "description": "Shopping",
                "amount": 300,
                "kind": "expense"
            }
        ]
    }

    income_response = client.get("/transactions?kind=income")

    assert income_response.status_code == 200
    assert income_response.json() == {
        "status": "ok",
        "transactions": [
            {
                "description": "Salary",
                "amount": 1000,
                "kind": "income"
            }
        ]
    }

def test_get_transactions_invalid_kind_filter_returns_400():
    response = client.get("/transactions?kind=banana")

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid kind"}




# This test below checks that the API save route writes to a file,

# but we do NOT want the test to create/modify a real project file.

#

# tmp_path:

# pytest gives this test a temporary folder.

# Any files created there are safe test files, not real project files.

#

# file_path = tmp_path / "transactions.json":

# creates a temporary path for a fake test version of transactions.json.

#

# monkeypatch.setattr("main.DATA_FILE", str(file_path)):

# temporarily replaces DATA_FILE inside main.py.

# "main.DATA_FILE" means: the DATA_FILE variable that lives in main.py.

# str(file_path) converts the Path object into a normal string path,

# which matches what save_to_file/open can safely use.

## tmp_path is a temporary test folder created by pytest.

# file_path = tmp_path / "transactions.json" creates a full temporary file path,

# not just the name "transactions.json".

#

# str(file_path) converts that full Path object into a normal string path.

# Example:

# C:...\Temp\pytest-...\transactions.json

#

# This keeps the test file separate from the real project transactions.json.


# So during this test only:

# main.DATA_FILE is not "transactions.json"

# main.DATA_FILE is the temporary test file path.

#

# After the test finishes, pytest restores the original DATA_FILE automatically.

def test_save_transactions_route_saves_to_file(tmp_path, monkeypatch):
    file_path = tmp_path / "transactions.json"
    monkeypatch.setattr("main.DATA_FILE", str(file_path))

    create_response = create_transaction()
    assert create_response.status_code == 201

    response = client.post("/transactions/save")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert file_path.exists()    

def test_load_transactions_route_loads_from_file(tmp_path, monkeypatch):
    file_path = tmp_path / "transactions.json"
    monkeypatch.setattr("main.DATA_FILE", str(file_path))

    file_path.write_text(
        '[{"description": "Salary", "amount": 1000, "kind": "income"}]'
    )

    before_response = client.get("/transactions")

    assert before_response.status_code == 200
    assert before_response.json() == {
        "status": "ok",
        "transactions": []
    }

    response = client.post("/transactions/load")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    transactions_response = client.get("/transactions")

    assert transactions_response.status_code == 200
    assert transactions_response.json() == {
        "status": "ok",
        "transactions": [
            {
                "description": "Salary",
                "amount": 1000,
                "kind": "income"
            }
        ]
    }

def test_load_transactions_missing_file_returns_400(tmp_path, monkeypatch):
    file_path = tmp_path / "missing.json"
    monkeypatch.setattr("main.DATA_FILE", str(file_path))

    response = client.post("/transactions/load")

    assert response.status_code == 404
    assert response.json() == {"detail": "File not found"}    


def test_load_transactions_invalid_json_returns_400(tmp_path, monkeypatch):
    file_path = tmp_path / "transactions.json"
    monkeypatch.setattr("main.DATA_FILE", str(file_path))

    file_path.write_text("not valid json")

    response = client.post("/transactions/load")

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON"}

def test_load_transactions_invalid_transaction_data_returns_400(tmp_path, monkeypatch):
    file_path = tmp_path / "transactions.json"
    monkeypatch.setattr("main.DATA_FILE", str(file_path))

    file_path.write_text(
        '[{"description": "Salary", "amount": true, "kind": "income"}]'
    )

    response = client.post("/transactions/load")

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid transaction data"}    

def test_load_transactions_is_atomic_when_file_has_invalid_record(tmp_path, monkeypatch):
    file_path = tmp_path / "transactions.json"
    monkeypatch.setattr("main.DATA_FILE", str(file_path))

    create_response = create_transaction("Existing", 50, "income")
    assert create_response.status_code == 201

    file_path.write_text(
        '[{"description": "Salary", "amount": 1000, "kind": "income"}, '
        '{"description": "Broken", "amount": true, "kind": "income"}]'
    )

    response = client.post("/transactions/load")

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid transaction data"}

    transactions_response = client.get("/transactions")

    assert transactions_response.status_code == 200
    assert transactions_response.json() == {
        "status": "ok",
        "transactions": [
            {
                "description": "Existing",
                "amount": 50,
                "kind": "income"
            }
        ]
    }

def test_transaction_summary_empty_ledger():
    response = client.get("/transactions/summary")

    assert response.status_code == 200
    assert response.json() == {
        "count": 0,
        "income_count": 0,
        "expense_count": 0,
        "balance": {
            "income": 0,
            "expense": 0,
            "balance": 0
        }
    } 

def test_transaction_summary_after_income_and_expense():
    income_response = create_transaction()
    assert income_response.status_code == 201

    expense_response = create_transaction("Rent", 300, "expense")
    assert expense_response.status_code == 201

    response = client.get("/transactions/summary")

    assert response.status_code == 200
    assert response.json() == {
        "count": 2,
        "income_count": 1,
        "expense_count": 1,
        "balance": {
            "income": 1000,
            "expense": 300,
            "balance": 700
        }
    }   

def test_summary_after_two_income_transactions_and_one_expense_transaction():
    income_response1 = create_transaction()
    assert income_response1.status_code == 201
    income_response2 = create_transaction("Bonus", 500, "income")  
    assert income_response2.status_code == 201
    expense_response = create_transaction("Rent", 300, "expense")  
    assert expense_response.status_code == 201
    response = client.get("/transactions/summary")
    assert response.status_code == 200
    assert response.json() == {
                           "count": 3,
                           "income_count": 2,
                           "expense_count": 1,
                           "balance": {
                                    "income": 1500,
                                    "expense": 300,
                                    "balance": 1200
                               }
                        }   

def test_get_transactions_returns_database_rows():
    salary_id = db.add_transaction("Salary", 4000, "income")
    assert salary_id == 1
    response = client.get("/transactions")
    assert response.status_code == 200
    assert response.json()=={
                       "status": "ok",
                       "transactions":[
                       {"id": 1,
                       "description": "Salary",
                       "amount": 4000.0,
                       "kind": "income"
                       }
                       ]
                    }

def test_get_transactions_filters_database_rows_by_kind():
    income_id = db.add_transaction("Salary", 4000, "income")
    assert income_id == 1
    expense_id = db.add_transaction("groceries", 300, "expense")
    assert expense_id == 2
    response = client.get("/transactions?kind=expense")
    assert response.status_code == 200
    assert response.json()=={
                       "status": "ok",
                       "transactions":[
                       {"id": expense_id,
                       "description": "groceries",
                       "amount": 300.0,
                       "kind": "expense"
                       }
                       ]
                    }

def test_get_transactions_invalid_kind_returns_400():
    response = client.get("/transactions?kind=food")
    assert response.status_code == 400
    assert response.json()=={"detail": "kind must be 'income' or 'expense'"}

def test_get_transactions_count_uses_database_rows():
    income_id = db.add_transaction("Salary", 4000, "income")
    assert income_id == 1
    expense_id = db.add_transaction("groceries", 300, "expense")
    assert expense_id == 2
    response = client.get("/transactions/count")
    assert response.status_code == 200
    assert response.json()=={"status": "ok", "count": 2}

def test_get_balance_uses_database_rows():
    income_id = db.add_transaction("Salary", 4000, "income")
    assert income_id == 1
    expense_id = db.add_transaction("groceries", 300, "expense")
    assert expense_id == 2

    response = client.get("/balance")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "balance": 3700.0}

def test_get_transactions_summary_uses_database_rows():
    income_id = db.add_transaction("Salary", 4000, "income")
    assert income_id == 1
    expense_id = db.add_transaction("groceries", 300, "expense")
    assert expense_id == 2

    response = client.get("/transactions/summary")

    assert response.status_code == 200
    assert response.json()=={
    "status": "ok",
    "count": 2,
    "income_count": 1,
    "expense_count": 1,
    "total_income": 4000.0,
    "total_expense": 300.0,
    "balance": 3700.0
}





    









    




