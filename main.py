from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import database_functions as db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.create_transactions_table()
    yield


app = FastAPI(lifespan=lifespan)


class TransactionInput(BaseModel):
    description: str
    amount: int | float
    kind: str

class AmountUpdate(BaseModel):
    amount: int | float



def raise_bad_request(error):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error)
    )


def raise_transaction_not_found():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Transaction not found"
    )


def transaction_row_to_dict(row):
    return {
        "id": row[0],
        "description": row[1],
        "amount": row[2],
        "kind": row[3] 
    }


@app.get("/")
def home():
    return {"message": "Budget Ledger API"}

@app.get("/balance")
def get_balance_endpoint():
    balance = db.get_balance()
    return {
        "status": "ok",
        "balance": balance
    }

@app.get("/transactions")
def get_transactions(kind: str | None = None):
    try:
        if kind is None:
            rows = db.get_all_transactions()
        else:
            rows = db.get_transactions_by_kind(kind)
    except ValueError as error:
        raise_bad_request(error)

    transactions = []

    for row in rows:
        transactions.append(transaction_row_to_dict(row))

    return {
        "status": "ok",
        "transactions": transactions
    }

@app.get("/transactions/count")
def get_transaction_count():
    rows = db.get_all_transactions()
    return {
         "status": "ok",
         "count": len(rows)
        }



@app.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_input: TransactionInput):
    try:
        new_id = db.add_transaction(
            transaction_input.description, 
            transaction_input.amount,
            transaction_input.kind
        )
    
    except ValueError as error:
        raise_bad_request(error)

    return {
      "status": "ok",
      "id": new_id
    }

@app.get("/transactions/summary")
def get_summary_endpoint():
    summary = db.get_full_summary()

    return {
        "status": "ok",
        **summary
    }

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    try:
        affected_rows = db.delete_transaction_by_id(transaction_id)

    except ValueError as error:
        raise_bad_request(error)
    if affected_rows == 0:
        raise_transaction_not_found()
    return {"status": "ok"}

@app.get("/transactions/{transaction_id}")
def find_transaction(transaction_id: int):
    try:
        row = db.get_transaction_by_id(transaction_id)
    except ValueError as error:
        raise_bad_request(error)
    if row is None:
        raise_transaction_not_found()
    return{
        "status": "ok",
        "transaction": transaction_row_to_dict(row)
    }

@app.patch("/transactions/{transaction_id}")
def update_transaction_amount(transaction_id: int, amount_update: AmountUpdate):
    try:
        affected_rows = db.update_transaction_by_id(transaction_id, amount_update.amount)
    except ValueError as error:
        raise_bad_request(error)
    if affected_rows == 0:
        raise_transaction_not_found()
    return {"status": "ok"}


