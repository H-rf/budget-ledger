from models import Transaction
import json

class BudgetLedger:
    def __init__(self):
        self.transactions = []

    def transaction_to_dict(self, transaction: Transaction) -> dict:
        return {
            "description": transaction.description,
            "amount": transaction.amount,
            "kind": transaction.kind}

    def is_valid_transaction_values(self, description, amount, kind) -> bool:
         return (
             type(description) == str
             and description != ""
             and self.is_valid_amount(amount)
             and (kind == "income" or kind == "expense")
            )

    def is_valid_amount(self, amount) -> bool:
        return (
             (type(amount) == int or type(amount) == float)
             and type(amount) != bool
             and amount > 0
            )

    def add_transaction(self, transaction: Transaction) -> dict:
        if not self.is_valid_transaction_values(transaction.description, transaction.amount, transaction.kind):
            return {"status": "error", "message": "Invalid transaction data"}
        self.transactions.append(transaction)
        return {"status": "ok"}

    def find_transaction(self, description: str) -> dict:
        for transaction in self.transactions:
            if transaction.description == description:
                return {
                  "status": "ok",
                  "transaction": self.transaction_to_dict(transaction)
                }

        return {"status": "error", "message": "Transaction not found"}

    def update_amount(self, description: str, new_amount: int | float) -> dict:
         if not self.is_valid_amount(new_amount):
             return {"status": "error", "message": "Invalid amount"}

         for transaction in self.transactions:
             if transaction.description == description:
                 transaction.amount = new_amount
                 return {"status": "ok"}

         return {"status": "error", "message": "Transaction not found"}

    
    def delete_transaction(self, description: str) -> dict:
        for transaction in self.transactions:
            if transaction.description == description:
                self.transactions.remove(transaction)
                return {"status": "ok"}
        return {"status": "error", "message": "Transaction not found"}


    def get_balance(self) -> dict:
        total_income = 0
        total_expense = 0
        for transaction in self.transactions:
            if transaction.kind == "income":
                total_income = total_income + transaction.amount
            if transaction.kind == "expense":
                total_expense = total_expense + transaction.amount

        balance = total_income - total_expense
        return {"income": total_income, "expense": total_expense, "balance": balance}

    def save_to_file(self, filename) -> dict:
        data = []
        for transaction in self.transactions:
            data.append(self.transaction_to_dict(transaction))
        with open(filename, "w") as file:
            json.dump(data, file)
        return {"status": "ok"}

    
    def load_from_file(self, filename) -> dict:
        loaded_transactions = []
        try:
            with open (filename, "r") as file:
                transactions = json.load(file)
        except FileNotFoundError:
            return {"status": "error", "message": "File not found"}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON"}


        try:
            for transaction_data in transactions:
                description = transaction_data["description"]
                amount = transaction_data["amount"]
                kind = transaction_data["kind"]
                if not self.is_valid_transaction_values(description, amount, kind):
                    return {"status": "error", "message": "Invalid transaction data"}
                loaded_transactions.append(Transaction(description, amount, kind))

        except KeyError:
            return {"status": "error", "message": "Missing transaction field"}

        self.transactions.extend(loaded_transactions)
        return {"status": "ok"}





