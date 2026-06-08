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

@app.get("/transactions")
def get_transactions():
    transactions = []

    for transaction in ledger.transactions:
        transactions.append(ledger.transaction_to_dict(transaction))

    return {
        "status": "ok",
        "transactions": transactions
    }