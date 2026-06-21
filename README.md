# Budget Ledger API

A small FastAPI + SQLite backend project for tracking income and expense transactions.

This project includes:

* SQLite database storage
* FastAPI HTTP routes
* Input validation
* CRUD operations
* Balance and summary calculations
* Recent transactions endpoint
* Unit tests for database functions
* API tests with FastAPI `TestClient`
* App startup database initialization

## Tech Stack

* Python
* FastAPI
* SQLite
* pytest
* Git

## Project Structure

```text
budget_checkpoint/
├── main.py
├── database_functions.py
├── test_database_functions.py
├── test_api.py
├── ARCHITECTURE.md
└── README.md
```

## Architecture

```text
Client / Browser / TestClient
→ main.py
→ database_functions.py
→ SQLite database
```

`main.py` handles HTTP routes and JSON responses.

`database_functions.py` handles validation, SQL queries, and database operations.

Tests use temporary SQLite databases so they do not depend on the real `budget.db`.

## Running the API

From the project folder:

```powershell
python -m uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

The `/docs` page provides an interactive Swagger UI for testing the API.

## Running Tests

Run all database and API tests:

```powershell
python -m pytest test_database_functions.py test_api.py -q
```

## Database

The app uses a local SQLite database:

```text
budget.db
```

The table is created automatically when the FastAPI app starts.

The database file should not be committed to Git.

## Transaction Shape

A transaction contains:

```json
{
  "id": 1,
  "description": "Salary",
  "amount": 4000.0,
  "kind": "income"
}
```

`kind` must be either:

```text
income
expense
```

`amount` must be a positive number.

`description` must be a non-empty string.

## API Endpoints

### Home

```http
GET /
```

Response:

```json
{
  "message": "Budget Ledger API"
}
```

---

### Create Transaction

```http
POST /transactions
```

Request body:

```json
{
  "description": "Salary",
  "amount": 4000,
  "kind": "income"
}
```

Response:

```json
{
  "status": "ok",
  "id": 1
}
```

---

### Get All Transactions

```http
GET /transactions
```

Response:

```json
{
  "status": "ok",
  "transactions": [
    {
      "id": 1,
      "description": "Salary",
      "amount": 4000.0,
      "kind": "income"
    }
  ]
}
```

---

### Filter Transactions by Kind

```http
GET /transactions?kind=income
```

or:

```http
GET /transactions?kind=expense
```

Invalid `kind` values return `400`.

---

### Get Transaction Count

```http
GET /transactions/count
```

Response:

```json
{
  "status": "ok",
  "count": 3
}
```

---

### Get Transaction Summary

```http
GET /transactions/summary
```

Response:

```json
{
  "status": "ok",
  "count": 3,
  "income_count": 2,
  "expense_count": 1,
  "total_income": 4500.0,
  "total_expense": 300.0,
  "balance": 4200.0
}
```

---

### Get Recent Transactions

```http
GET /transactions/recent?limit=5
```

Returns the newest transactions first, using highest `id` as newest.

Example:

```http
GET /transactions/recent?limit=2
```

Response:

```json
{
  "status": "ok",
  "transactions": [
    {
      "id": 3,
      "description": "Bonus",
      "amount": 500.0,
      "kind": "income"
    },
    {
      "id": 2,
      "description": "Groceries",
      "amount": 300.0,
      "kind": "expense"
    }
  ]
}
```

Rules:

* If `limit` is missing, it defaults to `5`.
* `limit` must be a positive integer.
* `limit=0` returns `400`.
* Non-integer values such as `limit=abc` return `422`.
* If `limit` is larger than the number of transactions, all available transactions are returned.

---

### Get Transaction by ID

```http
GET /transactions/{transaction_id}
```

Example:

```http
GET /transactions/1
```

Response:

```json
{
  "status": "ok",
  "transaction": {
    "id": 1,
    "description": "Salary",
    "amount": 4000.0,
    "kind": "income"
  }
}
```

Missing transactions return `404`.

Invalid IDs return `400`.

---

### Update Transaction Amount

```http
PATCH /transactions/{transaction_id}
```

Example:

```http
PATCH /transactions/1
```

Request body:

```json
{
  "amount": 4500
}
```

Response:

```json
{
  "status": "ok"
}
```

Missing transactions return `404`.

Invalid IDs or invalid amounts return `400`.

---

### Delete Transaction

```http
DELETE /transactions/{transaction_id}
```

Example:

```http
DELETE /transactions/1
```

Response:

```json
{
  "status": "ok"
}
```

Missing transactions return `404`.

Invalid IDs return `400`.

## Testing Strategy

The project has two test layers.

### Database Tests

`test_database_functions.py` checks the database layer directly:

* validation
* inserts
* selects
* updates
* deletes
* balance
* summary
* recent transactions

### API Tests

`test_api.py` checks the FastAPI routes through `TestClient`:

* response status codes
* response JSON shape
* route behavior
* invalid input handling
* integration between API routes and database functions

## Current Status

Implemented:

* Add transaction
* Get all transactions
* Filter by kind
* Count transactions
* Get balance
* Get summary
* Get transaction by ID
* Update amount
* Delete transaction
* Get recent transactions
* Automated tests
* Manual `/docs` smoke test
* Startup table creation

## Notes

This is a learning project focused on backend fundamentals:

* clear separation between API layer and database layer
* SQL parameter usage
* validation
* tests
* Git workflow
* route design
* small feature implementation
