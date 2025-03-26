from fastapi import APIRouter, Depends, Request, status
from app.models.schemas import APIResponse, AccountCreate, Account, TransferRequest
from app.services.banking_service import BankingService
import logging
from app.utils.exceptions import SelfTransferException
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["banking"])


def get_banking_service(request: Request)->BankingService:
    """Dependency injection function to provide BankingService instance.
    
    Args:

        request (Request): The FastAPI request object containing app state
        
    Returns:

        BankingService: The banking service instance from app state
    """
    return request.app.state.banking_service

@router.post("/accounts", response_model=APIResponse,status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    service: BankingService = Depends(get_banking_service),
):
    """Create a new bank account for a customer.
    
    Args:

        account (AccountCreate): The account creation request containing customer_id and initial_deposit.

        service (BankingService): The banking service dependency.
        
    Returns:

        APIResponse: Response containing the created account details.
        
    Raises:

        CustomerNotFoundException: If the customer_id doesn't exist.

        ValueError: If initial_deposit has more than 2 decimal places.
    """

    created_account = service.create_account(account.customer_id, account.initial_deposit)
    account = Account(**created_account)
    return APIResponse(
        status= "success",
        data= account,
        message = "Account created successfully",
        timestamp=datetime.now(timezone.utc)
    )

@router.post(path="/transfers", response_model=APIResponse)
async def transfer_amount(
    transfer: TransferRequest,
    service: BankingService = Depends(get_banking_service),
):
    """Execute a transfer between two accounts.
    
    Args:

        transfer (TransferRequest): Transfer details including from_account_id, to_account_id, and transfer_amount.

        service (BankingService): The banking service dependency.
        
    Returns:

        APIResponse: Response containing the transfer details.
        
    Raises:

        SelfTransferException: If from_account_id equals to_account_id.

        AccountNotFoundException: If either account doesn't exist.

        InsufficientFundsException: If source account has insufficient funds.

        ValueError: If transfer_amount has more than 2 decimal places.
    """
    if transfer.from_account_id == transfer.to_account_id:
        raise SelfTransferException()
    transfer_response = service.execute_transfer(transfer.from_account_id, transfer.to_account_id, transfer.transfer_amount)
    return APIResponse(
        status= "success",
        data= transfer_response,
        message = "Transfer executed successfully",
        timestamp=datetime.now(timezone.utc)
    )

@router.get("/accounts/{account_id}/balance", response_model=APIResponse)
async def get_balance(
    account_id: str,
    service: BankingService = Depends(get_banking_service),
):
    """Retrieve the current balance for a specific account.
    
    Args:

        account_id (str): The ID of the account to check.

        service (BankingService): The banking service dependency.
        
    Returns:

        APIResponse: Response containing the account ID and current balance.
        
    Raises:

        AccountNotFoundException: If the account_id doesn't exist.
    """
    balance = service.get_balance(account_id)
    balance_response = {
        "account_id": account_id,
        "current_balance": balance
    }
    return APIResponse(
        status= "success",
        data= balance_response,
        message = "Account balance retrieved successfully",
        timestamp=datetime.now(timezone.utc)
    )

@router.get("/accounts/{account_id}/transfers", response_model=APIResponse)
async def get_transfer_history(
    account_id: str,
    service: BankingService = Depends(get_banking_service),
):
    """Retrieve the transfer history for a specific account.
    
    Args:

        account_id (str): The ID of the account to get transfer history for.

        service (BankingService): The banking service dependency.
        
    Returns:

        APIResponse: Response containing the list of transfers.
        
    Raises:

        AccountNotFoundException: If the account_id doesn't exist.
    """

    transfer_history_response = service.get_transfers(account_id)
    return APIResponse(
    status= "success",
        data= transfer_history_response,
        message = "Transaction History retrieved successfully",
        timestamp=datetime.now(timezone.utc)
    )
