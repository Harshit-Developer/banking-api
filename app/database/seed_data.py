# app/database/seed_data.py
"""Pre-defined initial data for the banking API."""

CUSTOMERS = {
    1: {"customer_id": 1, "name": "Arisha Barron", "email":"Arisha@dummy.com"},
    2: {"customer_id": 2, "name": "Branden Gibson","email":"Branden@dummy.com"},
    3: {"customer_id": 3, "name": "Rhonda Church","email":"Rhonda@dummy.com"},
    4: {"customer_id": 4, "name": "Georgina Hazel","email":"Georgina@dummy.com"}
}

ACCOUNTS = {
    "acc1-1234": {"id": "acc1-1234", "customer_id": 1, "balance": 1000.00},
    "acc2-5678": {"id": "acc2-5678", "customer_id": 2, "balance": 500.00},
    "acc3-9012": {"id": "acc3-9012", "customer_id": 3, "balance": 750.50},
    "acc4-3456": {"id": "acc4-3456", "customer_id": 4, "balance": 2000.75},
    "acc5-7890": {"id": "acc5-7890", "customer_id": 1, "balance": 250.00},  
}

TRANSFERS = [
    {
        "transaction_id": "txn1-1111",
        "from_account_id": "acc1-1234",
        "to_account_id": "acc2-5678",
        "transfer_amount": 200.00,
        "timestamp": "2025-03-23T10:00:00",
    },
]