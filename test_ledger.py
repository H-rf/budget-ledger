from models import Transaction
from ledger import BudgetLedger

def test_validation_accepts_valid_transaction():
    ledger = BudgetLedger()
    assert ledger.is_valid_transaction_values("Salary", 1000, "income")

def test_validation_rejects_empty_description():
    ledger = BudgetLedger()
    assert not ledger.is_valid_transaction_values("", 500, "income")

def test_validation_rejects_invalid_amount_type():
    ledger = BudgetLedger()
    assert not ledger.is_valid_transaction_values("Entertainment", "150", "expense")
    
def test_validation_rejects_bool_amount():
    ledger = BudgetLedger()
    assert not ledger.is_valid_transaction_values("Entertainment", True, "expense")


def test_validation_rejects_zero_or_negative_amount():
    ledger1 = BudgetLedger()
    assert not ledger1.is_valid_transaction_values("Entertainment", 0, "expense")
    ledger2 = BudgetLedger()
    assert not ledger2.is_valid_transaction_values("Entertainment", -150, "expense")


def test_validation_rejects_invalid_kind():
    ledger = BudgetLedger()
    assert not ledger.is_valid_transaction_values("Salary", 1000, "check")


def test_add_valid_transaction():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    assert ledger.add_transaction(transaction1)=={"status": "ok"}
    assert ledger.add_transaction(transaction2)=={"status": "ok"}
    assert len(ledger.tasks)==2


def test_add_rejects_invalid_transaction():
    ledger = BudgetLedger()
    transaction =("", 500, "income")
    assert ledger.add_transaction(transaction)=={"status": "error", "message": "Invalid transaction data"}
    assert len(ledger.tasks)==0
    ledger0 = BudgetLedger()
    transaction0=("Entertainment", "150", "expense")
    assert ledger0.add_transaction(transaction0)=={"status": "error", "message": "Invalid transaction data"}
    assert len(ledger0.tasks)==0
    ledgerX = BudgetLedger()
    transactionX=("Entertainment", True, "expense")
    assert ledgerX.add_transaction(transactionX)=={"status": "error", "message": "Invalid transaction data"}
    assert len(ledgerX.tasks)==0
    ledger1 = BudgetLedger()
    transaction1=("Entertainment", 0, "expense")
    assert ledger1.add_transaction(transaction1)=={"status": "error", "message": "Invalid transaction data"}
    assert len(ledger1.tasks)==0
    ledger2 = BudgetLedger()
    transaction2=("Entertainment", -150, "expense")
    assert ledger2.add_transaction(transaction2)=={"status": "error", "message": "Invalid transaction data"}
    assert len(ledger2.tasks)==0
    ledger3 = BudgetLedger()
    transaction3=("Salary", 1000, "check")
    assert ledger3.add_transaction(transaction3==){"status": "error", "message": "Invalid transaction data"}
    assert len(ledger3.tasks)==0

def test_find_transaction_first_item():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    assert len(ledger.tasks)==2
    assert ledger.find_transaction("Salary")=={"status": "ok","transaction":{"description": "Salary","amount": 1000,"kind": "income"}}

def test_find_transaction_non_first_item():
    ledger = BudgetLedger()
    transaction1=("Grocery", 400, "expense")
    transaction2=("Salary", 1000, "income")
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    assert len(ledger.tasks)==2
    assert ledger.transactions[0].description == "Grocery"
    assert ledger.find_transaction("Salary")=={"status": "ok","transaction":{"description": "Salary","amount": 1000,"kind": "income"}}


def test_find_transaction_missing():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    assert len(ledger.tasks)==2
    assert ledger.find_transaction("Profit")=={"status": "error", "message": "Transaction not found"}


def test_update_amount_success():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    assert len(ledger.tasks)==2
    assert ledger.update_amount("Salary", 3000)=={"status": "ok"}
    assert ledger.tasks[0].amount == 3000
    assert ledger.tasks[1].amount == 400



def test_update_amount_rejects_invalid_amount():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    assert len(ledger.tasks)==2
    assert ledger.update_amount("Salary", -1000)=={"status": "error", "message": "Invalid amount"}
    assert ledger.tasks[0].amount == 1000
    assert ledger.tasks[1].amount == 400


def test_update_amount_missing_transaction():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    assert len(ledger.tasks)==2
    assert ledger.update_amount("Profit", 1000)=={"status": "error", "message": "Transaction not found"}
    assert ledger.tasks[0].amount == 1000
    assert ledger.tasks[1].amount == 400

def test_delete_transaction_success():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    assert len(ledger.tasks)==2
    assert ledger.delete_transaction("Salary")=={"status": "ok"}
    assert len(ledger.tasks)==1
    assert ledger.tasks[0]==("Grocery", 400, "expense")


def test_delete_transaction_missing():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    assert len(ledger.tasks)==2
    assert ledger.delete_transaction("Profit")=={"status": "error", "message": "Transaction not found"}
    assert len(ledger.tasks)==2


def test_get_balance_mixed_transactions():
    ledger = BudgetLedger()
    transaction1=("Salary", 1000.5, "income")
    transaction2=("Grocery", 400, "expense")
    transaction3=("Entertainment", -150, "expense")
    transaction4=("", 500, "income")
    transaction5=("Salary2", 1000, "income")
    transaction6=("Grocery2", 400, "expense")  
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    ledger.add_transaction(transaction3)
    ledger.add_transaction(transaction4)
    ledger.add_transaction(transaction5)
    ledger.add_transaction(transaction6)
    assert ledger.get_balance=={"income": 2000.5,
                "expense": 800,
                "balance": 1199.5}


def test_get_balance_empty_ledger():
    ledger = BudgetLedger()
    assert ledger.get_balance=={"income": 0,
                "expense": 0,
                "balance": 0}
def test_save_and_load_success(tmp_path):
    ledger = BudgetLedger()
    file_path= tmp_path/'Transactions.json'
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    transaction3=("Entertainment", -150, "expense")
    transaction4=("", 500, "income")
    transaction5=("Salary2", 1000, "income")
    transaction6=("Grocery2", 400, "expense")  
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    ledger.add_transaction(transaction3)
    ledger.add_transaction(transaction4)
    ledger.add_transaction(transaction5)
    ledger.add_transaction(transaction6)
    assert ledger.save_to_file(file_path)=={"status": "ok"}
def test_load_missing_file(tmp_path):
    file_path= tmp_path/'missing.json'
    ledger = BudgetLedger()
    assert ledger.load_from_file(file_path)=={"status": "error", "message": "File not found"}
    assert len(ledger.transactions) == 0


def test_load_invalid_json(tmp_path):
    ledger = BudgetLedger()
    file_path= tmp_path/'Invalid.json'
    file_path.write("not jason")
    assert ledger.load_from_file(file_path)=={"status": "error", "message": "Invalid JSON"}


def test_load_missing_field(tmp_path):
    ledger = BudgetLedger()
    file_path= tmp_path/'missing field.json'
    file_path.write('[{"title": "Study", "amount": 200}]')
    assert ledger.load_from_file(file_path)=={"status": "error", "message": "Missing transaction field"}


def test_load_invalid_transaction_data(tmp_path):
    ledger = BudgetLedger()
    file_path= tmp_path/'invalid data.json'
    file_path.write('[{"title": "Study", "amount": 200, "kind":"income},{"title": "Study", "amount": True, "kind":"income"}]')
    assert ledger.load_from_file(file_path)=={"status": "error", "message": "Invalid transaction data"}



def test_load_is_atomic_when_later_record_invalid(tmp_path):
    ledger = BudgetLedger()
    file_path= tmp_path/'atomic.json'
    transaction1=("Salary", 1000, "income")
    transaction2=("Grocery", 400, "expense")
    transaction3=("Entertainment", -150, "expense")
    transaction4=("", 500, "income")
    transaction5=("Salary2", 1000, "income")
    transaction6=("Grocery2", 400, "expense")  
    ledger.add_transaction(transaction1)
    ledger.add_transaction(transaction2)
    ledger.add_transaction(transaction3)
    ledger.add_transaction(transaction4)
    ledger.add_transaction(transaction5)
    ledger.add_transaction(transaction6)
    assert ledger.save_to_file(file_path)=={"status": "ok"}
    ledger2 = BudgetLedger()
    ledger2.load_from_file(file_path)
    assert len(ledger2.tasks)==4

