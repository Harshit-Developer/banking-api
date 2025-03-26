## Banking API

An internal HTTP API for a fake financial institution, built with Python and FastAPI. This project provides basic banking functionality, including account creation, transfers, balance retrieval, and transfer history.

## Project Overview

This API is designed to serve as a backend for financial institutions and is consumable by multiple frontends (web, iOS, Android, etc.). It fulfills the following core requirements:

Create bank accounts with initial deposits for customers.
Transfer amounts between any two accounts (same or different customers).
Retrieve account balances.
Retrieve transfer history for an account.

Built within a time constraint (4-5 hours), this is a prototype with an in-memory database and basic features, tested thoroughly but not fully production-ready. [Check Here.](#production-readiness-gaps)

## Architecture
The application follows a layered design:

 - Routers (routers/routes.py): Define API endpoints using FastAPI.
 - Services (services/banking_services.py): Encapsulate business logic (e.g., transfer validation, balance updates).
 - Models (models/schemas.py): Pydantic schemas for request/response validation.
 - Database (database/): In-memory storage with thread-safe operations and db handler to mock db operations.
 - Utils (utils/): Custom exceptions and handlers for error management.
 - Interaction: Requests hit endpoints, which delegate to the BankingService (injected via dependency), interacting with the in-memory DB.

## Project Structure
```bash
banking-api-tvkcba/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app setup and lifecycle management
│   ├── database/           # In-memory DB and pre-populated seed data
│   ├── models/             # Pydantic schemas (schemas.py)
│   ├── routers/            # API endpoint definitions (routes.py)
│   ├── services/           # Business logic implementation (service.py)
│   ├── tests/              # Unit tests (mirrored in tests.py)
│   ├── utils/              # Custom exceptions and handlers
├── tests.py                # Comprehensive test suite
├── requirements.txt        # Python dependencies
├── Dockerfile              # Runtime container configuration
├── Dockerfile.test         # Test container configuration
├── .env.example            # Example environment variables
└── README.md               # This documentation
````
## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized setup/testing)
- Git

### Local Setup
- Clone the Repository
```bash
git clone http://entrix-wpgiyt@git.codesubmit.io/entrix/banking-api-tvkcba
cd banking-api-tvkcba
````
- Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
````
- Install Dependencies
```bash
pip install -r requirements.txt
````
- (Optional) Configure Environment Variables:
 ```bash
cp .env.example .env   # On windows:- copy .env.example .env
````
  - Edit .env if desired (e.g., LOG_LEVEL=DEBUG). Defaults to INFO if omitted.

- Run the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
````
- Local Testing
```bash
pytest tests.py -v
````
  - Access the API at http://localhost:8000
  - Interactive API docs (Swagger UI) are available at http://localhost:8000/docs.


## Docker Setup ( Optional. You should have docker installed for this setup)
- Build and Run the Container
```bash
docker build -t banking-api .
docker run -d -p 8000:8000 --name banking-api -e LOG_LEVEL=INFO banking-api
````
- Run Tests in Docker
```bash
docker build -f Dockerfile.test -t banking-api-test .
docker run --rm banking-api-test
````
## Pre-populated Data

The API uses an in-memory database pre-loaded with the following data for testing endpoints:

### Customers
| Customer ID | Name            | Email                |
|-------------|-----------------|----------------------|
| 1           | Arisha Barron   | Arisha@dummy.com     |
| 2           | Branden Gibson  | Branden@dummy.com    |
| 3           | Rhonda Church   | Rhonda@dummy.com     |
| 4           | Georgina Hazel  | Georgina@dummy.com   |


 ### ACCOUNTS
| ACCOUNT ID  | Customer ID     | Balance              |
|-------------|-----------------|----------------------|
| acc1-1234   | 1               | 1000.00              |
| acc2-5678   | 2               | 500.00               |
| acc3-9012   | 3               | 750.50               |
| acc4-3456   | 4               | 200.75               |
| cc5-7890    | 1               | 250.50               |

 ### TRANSFERS
| Transaction ID | From Account ID | To Account ID | Amount | Timestamp            |
|----------------|-----------------|---------------|--------|----------------------|
| txn1-1111      | acc1-1234       | acc2-5678     | 200.00 | 2025-03-23T10:00:00  |
  
## API Endpoints
### Create a New Account
- Endpoint: POST /api/v1/accounts
- Example Request Body:
```json
{
  "customer_id": 1,
  "initial_deposit": 100.50
}
````
- Response (201 Created):
```json
{
    "status": "success",
    "data": {
        "account_id": "acc-7cd76af5",
        "customer_id": 1,
        "balance": 100.50
    },
    "message": "Account created successfully",
    "error_code": null,
    "timestamp": "2025-03-25T20:55:31.112236Z"
}
````
### Transfer Amounts
- Endpoint: POST POST /api/v1/transfers
- Example Request Body:
```json
{
  "from_account_id": "acc-abc12345",
  "to_account_id": "acc-def67890",
  "transfer_amount": 50.00
}
````
- Response (200 OK):
```json
{
    "status": "success",
    "data": {
        "transaction_id": "ccf78070-511a-40a4-a634-384b68c08fb1",
        "from_account_id": "acc-abc12345",
        "to_account_id": "acc-def67890",
        "transfer_amount": 100.0,
        "timestamp": "2025-03-25T20:56:42.463262"
    },
    "message": "Transfer executed successfully",
    "error_code": null,
    "timestamp": "2025-03-25T20:56:42.463453Z"
}
````
### Retrieve Balance
- Endpoint: GET /api/v1/accounts/{account_id}/balance
- Example: GET /api/v1/accounts/acc1-1234/balance
- Response (200 OK):
```json
{
    "status": "success",
    "data": {
        "account_id": "acc1-1234",
        "current_balance": 1000.0
    },
    "message": "Account balance retrieved successfully",
    "error_code": null,
    "timestamp": "2025-03-25T22:26:22.185432Z"
}
````
### Retrieve Transfer History
- Endpoint: GET /api/v1/accounts/{account_id}/transfers
- Example: GET /api/v1/accounts/acc1-1234/transfers
- Response (200 OK):
```json
{
    "status": "success",
    "data": [
        {
            "transaction_id": "txn1-1111",
            "from_account_id": "acc1-1234",
            "to_account_id": "acc2-5678",
            "transfer_amount": 200.0,
            "timestamp": "2025-03-23T10:00:00"
        }
    ],
    "message": "Transaction History retrieved successfully",
    "error_code": null,
    "timestamp": "2025-03-25T22:27:53.379071Z"
}
````

## Environment Variables
The app uses environment variables for configuration, loaded via python-dotenv. See .env.example:

 - LOG_LEVEL: Logging level (e.g., INFO, DEBUG). Defaults to INFO if unset.
 - Local: Set via .env file.
 - Docker: Pass via -e flag (e.g., -e LOG_LEVEL=DEBUG).

## Production Readiness Gaps
Due to the time constraint, this project makes compromises for simplicity, logic implementation, and functional implementations. Below are the gaps and steps to make it production-ready:

1. In-Memory Database
 - Current: Uses an in-memory dictionary with a Lock for thread safety.
 - Gap: No persistence; data is lost on restart.
 - Fix: Replace with a database (e.g., PostgreSQL) using SQLAlchemy for persistence and scalability.

2. Authentication and Authorization:
 - Current: No access control; anyone can use the API.
 - Gap: Internal APIs require employee authentication.
 - Fix: Implement OAuth2 or JWT to restrict access to authenticated users.

3. Transaction Safety:
 - Current: Transfers use a Lock for in-memory consistency, but not true ACID transactions.
 - Gap: Risk of partial updates in a real DB without transaction support.
 - Fix: Use database transactions in execute_transfer to ensure atomicity (e.g., rollback on failure).

4. Security:
 - Current: Basic input validation via Pydantic, but no rate limiting.
 - Gap: Vulnerable to abuse (e.g., DDoS).
 - Fix: Add rate limiting (e.g., slowapi).

5. Monitoring and Logging:
 - Current: Basic logging to console.
 - Gap: No centralized logging or monitoring for production issues.
 - Fix: Integrate with a logging service (e.g., Prometheus + Grafana) and add a /health endpoint for monitoring.
   
 6. Scalability:
 - Current: Single-threaded in-memory DB limits concurrent users.
 - Gap: Won’t scale to real-world banking loads.
 - Fix: Use a distributed DB and deploy with a load balancer.

### Design Choices
 - FastAPI: Selected for its async capabilities, auto-generated Swagger UI, and Pydantic integration, enabling rapid 
 - development and built-in documentation within 4 hours.
 - In-Memory DB: Chosen to avoid complex DB setup, prioritizing functional endpoints and testing within the time limit.
 - Pydantic Models: Used for strict input validation (e.g., 2-decimal precision) and clear API schemas, reducing errors.
 - Testing: Comprehensive pytest suite ensures reliability, leveraging pytest-asyncio for async endpoints.
 - Docker: Included for reproducible deployment and testing, enhancing out-of-the-box usability despite time constraints.

### Note:
This is a prototype assignment. For production use, address the gaps above to enhance functionality.
