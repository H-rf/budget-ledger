from fastapi import FastAPI
from pydantic import BaseModel

from ledger import BudgetLedger
from models import Transaction


app = FastAPI()

ledger = BudgetLedger()


class TransactionInput(BaseModel):
    description: str
    amount: int | float
    kind: str

@app.get("/")
def home():
    return {"message": "Budget Ledger API"}


@app.get("/balance")
def get_balance():
    return ledger.get_balance()

@app.get("/transactions")
def get_transactions():
    transactions = []

    for transaction in ledger.transactions:
        transactions.append(ledger.transaction_to_dict(transaction))

    return {
        "status": "ok",
        "transactions": transactions
    }

@app.post("/transactions")
def create_transaction(transaction_input: TransactionInput):
    transaction = Transaction(
        transaction_input.description,
        transaction_input.amount,
        transaction_input.kind
    )

    result = ledger.add_transaction(transaction)

    return result

@app.delete("/transactions/{description}")
def delete_transaction(description: str):
            ledger.delete_transaction(description)

@app.get("/transactions/{description}")
def find_transaction(description: str):
    return ledger.find_transaction(description)            
