import pytest
from fastapi.testclient import TestClient

from main import app, ledger

client = TestClient(app)


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
