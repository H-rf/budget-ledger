# Budget API Architecture

## Current Final Flow
Client/TestClient sends HTTP request
→ main.py receives route
→FastAPI/Pydantic validates request shape and parameter types.
→database_functions.py validates business rules.
→ main.py calls database_functions.py
→ database_functions.py talks to SQLite
→ main.py returns JSON response
### Example: `POST /transactions`

Client/TestClient sends:

```json
{
  "description": "Salary",
  "amount": 4000,
  "kind": "income"
}
```

Flow:

```text
POST /transactions
→ main.py matches create_transaction()
→ TransactionInput validates request body shape and types
→ create_transaction() extracts transaction_input.description, transaction_input.amount, transaction_input.kind
→ db.add_transaction(description, amount, kind)
→ database_functions.py validates business rules:
   - description must be non-empty
   - amount must be positive
   - kind must be "income" or "expense"
→ SQLite inserts a row into transactions table
→ database returns new_id
→ main.py returns {"status": "ok", "id": new_id}
```

### Example: `GET /transactions/1`

Client/TestClient sends:

```text
GET /transactions/1
```

Flow:

```text
GET /transactions/1
→ main.py matches find_transaction(transaction_id: int)
→ FastAPI validates transaction_id is an integer
→ db.get_transaction_by_id(transaction_id)
→ database_functions.py validates transaction_id is a positive integer
→ SQLite searches for row with id = 1
→ if row exists, database returns a tuple like (1, "Salary", 4000.0, "income")
→ transaction_row_to_dict(row) converts tuple into JSON-ready dictionary
→ main.py returns {"status": "ok", "transaction": {...}}
```

### Example: Invalid ID

Client/TestClient sends:

```text
GET /transactions/0
```

Flow:

```text
GET /transactions/0
→ FastAPI accepts 0 as an integer
→ db.get_transaction_by_id(0)
→ validate_transaction_id(0) raises ValueError("transaction_id must be a positive integer")
→ main.py catches ValueError
→ raise_bad_request(error)
→ API returns 400 with {"detail": "transaction_id must be a positive integer"}
```

### Example: Missing Transaction

Client/TestClient sends:

```text
GET /transactions/999
```

Flow:

```text
GET /transactions/999
→ FastAPI validates 999 is an integer
→ db.get_transaction_by_id(999)
→ SQLite searches for id = 999
→ no row is found
→ database returns None
→ main.py sees row is None
→ raise_transaction_not_found()
→ API returns 404 with {"detail": "Transaction not found"}
```


## Old System: ledger.py
- ledger.py was the first implementation.
- It stored transactions in memory using Python objects/lists.
- It was useful for learning business logic before API/database complexity.
- It had functions like add, update, delete, find, balance.
- It is now old architecture because SQLite replaced it as the active storage system.
- It may stay as reference, but main.py should no longer depend on it.


## New System: database_functions.py
- database_functions.py is the active storage layer now.
- It talks to SQLite instead of storing objects in memory.
- It creates the transactions table.
- It inserts, selects, updates, and deletes rows.
- It validates business rules before touching the database.
- It returns simple values: rows, ids, affected row counts, balances, summaries.
- main.py calls these functions instead of calling ledger.py.


## API Layer: main.py
- main.py is the HTTP/API layer.
- It defines FastAPI routes like GET, POST, PATCH, and DELETE.
- It receives requests from the client or TestClient.
- It uses Pydantic models like TransactionInput and AmountUpdate to validate request bodies.
- It calls database_functions.py to do the actual database work.
- It converts database rows into JSON-ready dictionaries.
- It converts internal errors into HTTP responses like 400 and 404.
- It should not contain old ledger.py logic anymore.


## Test Layers
- test_database_functions.py tests database_functions.py directly.
- It checks SQLite behavior without going through FastAPI.
- test_api.py tests the API routes through TestClient.
- API tests use a temporary SQLite database through tmp_path and monkeypatch.
- The temp_db fixture prevents tests from changing the real budget.db.
- Some API tests seed data directly with db.add_transaction to isolate GET routes.
- POST/PATCH/DELETE tests use client requests because those routes are the behavior being tested.
- Passing both test files proves both the database layer and API layer work together.


## What Was Removed
- main.py no longer imports BudgetLedger.
- main.py no longer creates ledger = BudgetLedger().
- main.py no longer uses Transaction objects from models.py.
- main.py no longer uses raise_http_error_for_result().
- JSON save/load routes were removed because SQLite now handles persistence.
- Old description-based routes were replaced with ID-based routes.
- ledger.py is now old reference architecture, not the active backend.


## Next Improvements
- Run all database and API tests before each major change.
- Keep budget.db out of Git because it is runtime data.
- Refactor repeated patterns when they become clear.
- Consider adding startup database initialization later.
- Consider moving repeated summary/count logic out of main.py later.
- Keep ARCHITECTURE.md updated when the project structure changes.
- Eventually remove or archive old ledger.py files if they are no longer needed.