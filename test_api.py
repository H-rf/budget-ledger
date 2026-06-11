import pytest
from fastapi.testclient import TestClient

from main import app, ledger

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

# This fixture keeps API tests independent from each other.

#

# The FastAPI app uses one global in-memory ledger object:

# ledger = BudgetLedger()

#

# If one test creates a transaction, that transaction stays inside

# ledger.transactions unless we manually clear it.

#

# Without this reset:

# Test A could create "Salary"

# Test B could expect an empty ledger

# Test B might fail because "Salary" is still there from Test A

#

# @pytest.fixture:

# tells pytest this function is test setup/cleanup support code.

#

# autouse=True:

# means pytest runs this fixture automatically for every test,

# even if the test does not mention reset_ledger by name.

#

# ledger.transactions.clear():

# empties the in-memory transaction list before each test starts.

#

# Result:

# every test begins with a clean ledger,

# so tests do not depend on leftovers from previous tests.

@pytest.fixture(autouse=True)
def reset_ledger():
    ledger.transactions.clear()


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











    




