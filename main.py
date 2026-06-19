from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

import database_functions as db

from ledger import BudgetLedger
from models import Transaction


app = FastAPI()

ledger = BudgetLedger()

DATA_FILE = "transactions.json"

def raise_http_error_for_result(result):
    if result["status"] != "error":
        return

    if result["message"] in ["Transaction not found", "File not found"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )

    if result["message"] in ["Invalid transaction data", "Invalid amount", "Invalid JSON"]:
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

    return {
      "status": "ok",
      "id": new_id
    }

@app.get("/transactions/summary")   
def get_summary_endpoint():
    expense_count = 0
    income_count = 0
    rows = db.get_all_transactions()
    for row in rows:
        if row[3] == "income":
            income_count+=1
        elif row[3] == "expense":
            expense_count+=1 
    summary = db.get_summary()            
    return {
        "status":"ok",
        "count":len(rows),
        "income_count":income_count,
        "expense_count":expense_count,
        "total_income": summary["income"],
        "total_expense": summary["expense"],
        "balance": summary["balance"]
      }    

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

@app.post("/transactions/save")
def save_transactions():
    result = ledger.save_to_file(DATA_FILE)
    raise_http_error_for_result(result)
    return result    

@app.post("/transactions/load")
def load_transactions():
    result = ledger.load_from_file(DATA_FILE)
    raise_http_error_for_result(result)
    return result


