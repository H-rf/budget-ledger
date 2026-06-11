\# Budget Ledger



A small Python project for tracking income and expense transactions.



\## Features



\- Add transactions

\- Validate transaction data

\- Find transactions by description

\- Update transaction amounts

\- Delete transactions

\- Calculate income, expenses, and balance

\- Save transactions to JSON

\- Load transactions from JSON

\- Prevent partial loading when invalid data is found



\## Project structure



\- `models.py` contains the `Transaction` class

\- `ledger.py` contains the `BudgetLedger` class

\- `test\_ledger.py` contains pytest tests



\## How to run tests



```bash

pytest

python -m pip install -r requirements.txt

## API Endpoints

- `GET /` — API welcome message
- `GET /balance` — get current income, expense, and balance
- `GET /transactions` — list all transactions
- `GET /transactions?kind=income` — list income transactions
- `GET /transactions?kind=expense` — list expense transactions
- `GET /transactions/count` — get transaction count
- `GET /transactions/summary` — get count, income count, expense count, and balance summary
- `GET /transactions/{description}` — find a transaction by description
- `POST /transactions` — create a transaction
- `PATCH /transactions/{description}` — update a transaction amount
- `DELETE /transactions/{description}` — delete a transaction
- `POST /transactions/save` — save transactions to file
- `POST /transactions/load` — load transactions from file

