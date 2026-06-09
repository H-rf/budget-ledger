from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from ledger import BudgetLedger
from models import Transaction


app = FastAPI()

ledger = BudgetLedger()


class TransactionInput(BaseModel):
    description: str
    amount: int | float
    kind: str

class AmountUpdate(BaseModel):
    amount: int | float

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

@app.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_input: TransactionInput):
    transaction = Transaction(
        transaction_input.description,
        transaction_input.amount,
        transaction_input.kind
    )
    result = ledger.add_transaction(transaction)

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    return result

@app.delete("/transactions/{description}")
def delete_transaction(description: str):
    result = ledger.delete_transaction(description)

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )

    return result

@app.get("/transactions/{description}")
def find_transaction(description: str):
    result = ledger.find_transaction(description)

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )

    return result

@app.patch("/transactions/{description}")
def update_transaction_amount(description: str, amount_update: AmountUpdate):
    return ledger.update_amount(description, amount_update.amount)                
