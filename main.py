from fastapi import FastAPI
from ledger import BudgetLedger

app = FastAPI()

ledger = BudgetLedger()


@app.get("/")
def home():
    return {"message": "Budget Ledger API"}


@app.get("/balance")
def get_balance():
    return ledger.get_balance()