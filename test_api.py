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








    




