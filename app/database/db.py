from typing import List, Optional
import uuid
import logging
from threading import Lock
from app.models.schemas import Transfer
from app.database.seed_data import CUSTOMERS, ACCOUNTS, TRANSFERS
from app.utils.exceptions import AccountNotFoundException

logger = logging.getLogger(__name__)

class Database:
    """In-memory database implementation for banking operations."""

    def __init__(self):
        """Initialize the database with seed data and thread-safe lock.
        
        Sets up initial state with customers, accounts, and transfers from seed data.
        Creates a threading Lock for concurrent access safety.
        """
        self.customers = CUSTOMERS.copy()
        self.accounts = ACCOUNTS.copy()
        self.transfers = [
            Transfer(**t) for t in TRANSFERS
        ]
        self.lock = Lock()
        logger.info("Initialized database with %d customers, %d accounts, %d transfers",
                    len(self.customers), len(self.accounts), len(self.transfers))

    def get_customer(self, customer_id: int) -> Optional[dict]:
        """Retrieve a customer by ID.
        
        Args:
            customer_id (int): The ID of the customer to fetch
            
        Returns:
            Optional[dict]: Customer details if found, None otherwise
        """
        return self.customers.get(customer_id)

    def get_account(self, account_id: str) -> Optional[dict]:
        """Retrieve an account by ID.
        
        Args:
            account_id (str): The ID of the account to fetch
            
        Returns:
            Optional[dict]: Account details if found, None otherwise
        """
        return self.accounts.get(account_id)

    def get_accounts_by_customer(self, customer_id: int) -> List[dict]:
        """Retrieve all accounts for a specific customer.
        
        Args:
            customer_id (int): The ID of the customer whose accounts to fetch
            
        Returns:
            List[dict]: List of account dictionaries belonging to the customer
        """
        return [acc for acc in self.accounts.values() if acc["customer_id"] == customer_id]

    def create_account(self, customer_id: int, initial_deposit: float) -> dict:
        """Create a new account for a customer.
        
        Args:
            customer_id (int): The ID of the customer to create account for
            initial_deposit (float): Initial balance for the new account
            
        Returns:
            dict: Newly created account details
        """
        with self.lock:
            account_id = f"acc-{uuid.uuid4().hex[:8]}"
            account = {"account_id": account_id, "customer_id": customer_id, "balance": initial_deposit}
            self.accounts[account_id] = account
            logger.info(f"Created account {account_id} for customer {customer_id} with balance {initial_deposit}")
            return account

    def get_balance(self, account_id: str) -> float:
        """Retrieve the current balance of an account.
        
        Args:
            account_id (str): The ID of the account to check
            
        Returns:
            float: Current balance of the account
            
        Raises:
            AccountNotFoundException: If the account_id doesn't exist
        """
        account = self.get_account(account_id)
        if not account:
            raise AccountNotFoundException(account_id)
        return account["balance"]

    def update_balance(self, account_id: str, amount: float):
        """Update an account's balance by adding the specified amount.
        
        Args:
            account_id (str): The ID of the account to update
            amount (float): Amount to add (positive) or subtract (negative) from balance
        """
        account = self.accounts.get(account_id)
        if account:
            account["balance"] += amount

    def add_transfer(self, transfer: Transfer):
        """Add a transfer record to the database.
        
        Args:
            transfer (Transfer): The transfer object to record
        """
        with self.lock:
            self.transfers.append(transfer)

    def get_transfers_by_account(self, account_id: str) -> List[Transfer]:
        """Retrieve all transfers involving a specific account.
        
        Args:
            account_id (str): The ID of the account to get transfers for
            
        Returns:
            List[Transfer]: List of transfers where account is sender or receiver
            
        Raises:
            AccountNotFoundException: If the account_id doesn't exist
        """
        if account_id not in self.accounts:
            raise AccountNotFoundException(account_id)
        return [t for t in self.transfers if t.from_account_id == account_id or t.to_account_id == account_id]

    def get_transfers_by_customer(self, customer_id: int) -> List[Transfer]:
        """Retrieve all transfers involving a customer's accounts.
        
        Args:
            customer_id (int): The ID of the customer to get transfers for
            
        Returns:
            List[Transfer]: List of transfers involving customer's accounts
            
        Raises:
            AccountNotFoundException: If the customer_id doesn't exist (repurposed exception)
        """
        if customer_id not in self.customers:
            raise AccountNotFoundException(str(customer_id))  # Repurposed for simplicity
        customer_accounts = [acc["id"] for acc in self.get_accounts_by_customer(customer_id)]
        return [t for t in self.transfers if t.from_account_id in customer_accounts or t.to_account_id in customer_accounts]