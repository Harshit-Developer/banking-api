import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import Database
from app.services.banking import BankingService
from app.models.banking import AccountCreate, TransferRequest

# Use pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio

# Fixture to set up the test client and mock database
@pytest.fixture
def client():
    # Create a fresh database instance for each test
    app.state.db = Database()
    app.state.banking_service = BankingService(app.state.db)
    return TestClient(app)

# Below we assume that seed_data has customer id '1'.
@pytest.fixture
def sample_customer_id():
    return 1  

# Test cases for /accounts endpoint
async def test_create_account_success(client, sample_customer_id):
    """Test successful account creation."""
    account_data = AccountCreate(customer_id=sample_customer_id, initial_deposit=100.50)
    response = client.post("/api/v1/accounts", json=account_data.model_dump())
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Account created successfully"
    assert data["data"]["customer_id"] == sample_customer_id
    assert data["data"]["balance"] == 100.50
    assert "account_id" in data["data"]
    assert isinstance(data["timestamp"], str)

async def test_create_account_invalid_customer(client):
    """Test account creation with non-existent customer."""
    account_data = AccountCreate(customer_id=999, initial_deposit=100.00)
    response = client.post("/api/v1/accounts", json=account_data.model_dump())
    
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert data["message"] == "Customer Id not found"

async def test_create_account_invalid_deposit_precision(client, sample_customer_id):
    """Test account creation with invalid decimal precision."""
    invalid_data = {
        "customer_id": sample_customer_id,
        "initial_deposit": 100.555  
    }
    response = client.post("/api/v1/accounts", json=invalid_data)
    assert response.status_code == 422  
    data = response.json()
    assert "Initial deposit must have at most 2 decimal places" in str(data["detail"])

# Test cases for /transfers endpoint
async def test_transfer_success(client, sample_customer_id):
    """Test successful transfer between accounts."""
    acc1 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=200.00).model_dump()).json()["data"]
    acc2 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=50.00).model_dump()).json()["data"]
    
    transfer_data = TransferRequest(
        from_account_id=acc1["account_id"],
        to_account_id=acc2["account_id"],
        transfer_amount=100.00
    )
    response = client.post("/api/v1/transfers", json=transfer_data.model_dump())
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Transfer executed successfully"
    assert data["data"]["from_account_id"] == acc1["account_id"]
    assert data["data"]["to_account_id"] == acc2["account_id"]
    assert data["data"]["transfer_amount"] == 100.00

async def test_transfer_self_transfer(client, sample_customer_id):
    """Test transfer to the same account."""
    acc = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=200.00).model_dump()).json()["data"]
    
    transfer_data = TransferRequest(
        from_account_id=acc["account_id"],
        to_account_id=acc["account_id"],
        transfer_amount=50.00
    )
    response = client.post("/api/v1/transfers", json=transfer_data.model_dump())
    
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "failure"
    assert data["msg"] == "Transfer cannot be completed. Cannot transfer money to the same account"

async def test_transfer_insufficient_funds(client, sample_customer_id):
    """Test transfer with insufficient funds."""
    acc1 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=50.00).model_dump()).json()["data"]
    acc2 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=0.00).model_dump()).json()["data"]
    
    transfer_data = TransferRequest(
        from_account_id=acc1["account_id"],
        to_account_id=acc2["account_id"],
        transfer_amount=100.00
    )
    response = client.post("/api/v1/transfers", json=transfer_data.model_dump())
    
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "failure"
    assert data["msg"] == "Transfer cannot be completed. Insufficient funds"

async def test_transfer_account_not_found(client, sample_customer_id):
    """Test transfer with non-existent account."""
    acc = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=200.00).model_dump()).json()["data"]
    
    transfer_data = TransferRequest(
        from_account_id=acc["account_id"],
        to_account_id="non-existent-id",
        transfer_amount=50.00
    )
    response = client.post("/api/v1/transfers", json=transfer_data.model_dump())
    
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert data["message"] == "Account not found"

# Test cases for /accounts/{account_id}/balance endpoint
async def test_get_balance_success(client, sample_customer_id):
    """Test retrieving account balance."""
    acc = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=150.75).model_dump()).json()["data"]
    
    response = client.get(f"/api/v1/accounts/{acc['account_id']}/balance")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Account balance retrieved successfully"
    assert data["data"]["account_id"] == acc["account_id"]
    assert data["data"]["current_balance"] == 150.75

async def test_get_balance_account_not_found(client):
    """Test retrieving balance for non-existent account."""
    response = client.get("/api/v1/accounts/non-existent-id/balance")
    
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert data["message"] == "Account not found"

# Test cases for /accounts/{account_id}/transfers endpoint
async def test_get_transfer_history_success(client, sample_customer_id):
    """Test retrieving transfer history."""
    acc1 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=200.00).model_dump()).json()["data"]
    acc2 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=0.00).model_dump()).json()["data"]
    
    transfer_data = TransferRequest(
        from_account_id=acc1["account_id"],
        to_account_id=acc2["account_id"],
        transfer_amount=50.00
    )
    client.post("/api/v1/transfers", json=transfer_data.model_dump())
    
    response = client.get(f"/api/v1/accounts/{acc1['account_id']}/transfers")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Transaction History retrieved successfully"
    assert len(data["data"]) == 1
    assert data["data"][0]["from_account_id"] == acc1["account_id"]
    assert data["data"][0]["to_account_id"] == acc2["account_id"]

async def test_get_transfer_history_account_not_found(client):
    """Test retrieving transfer history for non-existent account."""
    response = client.get("/api/v1/accounts/non-existent-id/transfers")
    
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert data["message"] == "Account not found"

# Additional edge cases for amount_precision and negative amount
async def test_transfer_amount_precision(client, sample_customer_id):
    """Test transfer with invalid amount precision."""
    acc1 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=200.00).model_dump()).json()["data"]
    acc2 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=0.00).model_dump()).json()["data"]
    
    transfer_data = {
        "from_account_id": acc1["account_id"],
        "to_account_id": acc2["account_id"],
        "transfer_amount": 50.555 
    }
    response = client.post("/api/v1/transfers", json=transfer_data)
    
    assert response.status_code == 422
    data = response.json()
    assert "Transfer amount must have at most 2 decimal places" in str(data["detail"])

async def test_transfer_negative_amount(client, sample_customer_id):
    """Test transfer with negative amount."""
    acc1 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=200.00).model_dump()).json()["data"]
    acc2 = client.post("/api/v1/accounts", json=AccountCreate(customer_id=sample_customer_id, initial_deposit=0.00).model_dump()).json()["data"]
    
    transfer_data = {
        "from_account_id": acc1["account_id"],
        "to_account_id": acc2["account_id"],
        "transfer_amount": -50.00
    }
    response = client.post("/api/v1/transfers", json=transfer_data)
    
    assert response.status_code == 422
    data = response.json()
    assert "greater than 0" in str(data["detail"])