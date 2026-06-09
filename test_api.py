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