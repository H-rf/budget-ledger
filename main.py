from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from ledger import BudgetLedger
from models import Transaction


app = FastAPI()

ledger = BudgetLedger()

def raise_http_error_for_result(result):
    if result["status"] != "error":
        return

    if result["message"] == "Transaction not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )

    if result["message"] in ["Invalid transaction data", "Invalid amount"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=result["message"]
    )


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
def get_transactions(kind: str | None = None):
    if kind is not None and kind not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid kind"
        )

    transactions = []

    for transaction in ledger.transactions:
        if kind is None or transaction.kind == kind:
            transactions.append(ledger.transaction_to_dict(transaction))

    return {
        "status": "ok",
        "transactions": transactions
    }

@app.get("/transactions/count")
def get_transaction_count():
    return {"count": len(ledger.transactions)}



@app.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_input: TransactionInput):
    transaction = Transaction(
        transaction_input.description,
        transaction_input.amount,
        transaction_input.kind
    )
    result = ledger.add_transaction(transaction)

    raise_http_error_for_result(result)

    return result

@app.delete("/transactions/{description}")
def delete_transaction(description: str):
    result = ledger.delete_transaction(description)

    raise_http_error_for_result(result)

    return result

@app.get("/transactions/{description}")
def find_transaction(description: str):
    result = ledger.find_transaction(description)

    raise_http_error_for_result(result)

    return result

@app.patch("/transactions/{description}")
def update_transaction_amount(description: str, amount_update: AmountUpdate):
    result = ledger.update_amount(description, amount_update.amount)
    raise_http_error_for_result(result)
    return result          
