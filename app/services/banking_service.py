from typing import List
from datetime import datetime
import uuid
import logging
from app.models.schemas import Transfer
from app.utils.exceptions import AccountNotFoundException, InsufficientFundsException,CustomerNotFoundException, SelfTransferException

logger = logging.getLogger(__name__)

class BankingService:
    """Service class handling banking operations and business logic."""

    def __init__(self, db):
        """Initialize the BankingService with a database instance.
        
        Args:
            db: Database instance for persistence operations
        """
        self.db = db

    def create_account(self, customer_id: int, initial_deposit: float) -> dict:
        """Create a new bank account for a customer.
        
        Args:
            customer_id (int): The ID of the customer to create an account for
            initial_deposit (float): Initial amount to deposit in the account
            
        Returns:
            dict: Created account details
            
        Raises:
            CustomerNotFoundException: If the customer_id doesn't exist in the database
        """
        if not self.db.get_customer(customer_id):
            logger.warning(f"Account creation failed: Customer {customer_id} not found")
            raise CustomerNotFoundException()  
        return self.db.create_account(customer_id, initial_deposit)

    def get_balance(self, account_id: str) -> float:
        """Retrieve the current balance for a specific account.
        
        Args:
            account_id (str): The ID of the account to check
            
        Returns:
            float: Current balance of the account
            
        Raises:
            AccountNotFoundException: If the account_id doesn't exist
        """
        return self.db.get_balance(account_id)  

    def get_transfers(self, account_id: str) -> List[Transfer]:
        """Retrieve all transfers associated with a specific account.
        
        Args:
            account_id (str): The ID of the account to get transfer history for
            
        Returns:
            List[Transfer]: List of Transfer objects representing account transactions
            
        Raises:
            AccountNotFoundException: If the account_id doesn't exist
        """
        return self.db.get_transfers_by_account(account_id)  

    def execute_transfer(self, from_account_id: str, to_account_id: str, transfer_amount: float) -> Transfer:
        """Execute a transfer between two accounts.
        
        Args:
            from_account_id (str): Source account ID
            to_account_id (str): Destination account ID
            transfer_amount (float): Amount to transfer
            
        Returns:
            Transfer: Transfer object containing transaction details
            
        Raises:
            AccountNotFoundException: If either account doesn't exist
            InsufficientFundsException: If source account has insufficient funds
            SelfTransferException: If source and destination accounts are the same
        """
         
        from_account = self.db.get_account(from_account_id)
        to_account = self.db.get_account(to_account_id)
        if not from_account:
            logger.warning(f"Transfer failed: Source account {from_account_id} not found")
            raise AccountNotFoundException()
        if not to_account:
            logger.warning(f"Transfer failed: Destination account {to_account_id} not found")                
            raise AccountNotFoundException()
        if from_account == to_account:
            logger.warning(f"Transfer failed: Destination account {to_account_id} and Source Account {from_account} are same.")
            raise SelfTransferException()

        if from_account["balance"] < transfer_amount:
            logger.warning(f"Transfer failed: Insufficient funds in {from_account_id}")
            raise InsufficientFundsException()

        self.db.update_balance(from_account_id, -transfer_amount)
        self.db.update_balance(to_account_id, transfer_amount)

        transfer_id = str(uuid.uuid4())
        timestamp = datetime.now()
        transfer = Transfer(
            transaction_id=transfer_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            transfer_amount=transfer_amount,
            timestamp=timestamp
        )
        self.db.add_transfer(transfer)
        logger.info(f"Transfer {transfer_id}: {transfer_amount} from {from_account_id} to {to_account_id}")
        return transfer