from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import AccountNotFoundException, CustomerNotFoundException, InsufficientFundsException, SelfTransferException

async def AccountNotFoundExceptionHandler(request:Request, exc: AccountNotFoundException) -> JSONResponse:
    """Handle AccountNotFoundException by returning a 404 JSON response.
    
    Args:
        request (Request): The FastAPI request object
        exc (AccountNotFoundException): The exception instance that was raised
        
    Returns:
        JSONResponse: A response with status 'failure' and appropriate message, status code 404
    """
    return JSONResponse(
        content={"status":"failure", "message": "Account not found"},
        status_code=404
    )

async def CustomerNotFoundExceptionHandler(request:Request, exc: CustomerNotFoundException) -> JSONResponse:
    """Handle CustomerNotFoundException by returning a 404 JSON response.
    
    Args:
        request (Request): The FastAPI request object
        exc (CustomerNotFoundException): The exception instance that was raised
        
    Returns:
        JSONResponse: A response with status 'failure' and appropriate message, status code 404
    """
    return JSONResponse(
        content={"status":"failure", "message": "Customer Id not found"},
        status_code=404
    )



async def InsufficientFundsExceptionHandler(request:Request, exc: InsufficientFundsException):
    """Handle InsufficientFundsException by returning a 400 JSON response.
    
    Args:
        request (Request): The FastAPI request object
        exc (InsufficientFundsException): The exception instance that was raised
        
    Returns:
        JSONResponse: A response with status 'failure' and appropriate message, status code 400
    """
    return JSONResponse(
        content={"status":"failure", "msg": "Transfer cannot be completed. Insufficient funds"},
        status_code=400
    )

async def SelfTransferExceptionHandler(request:Request, exc: SelfTransferException):
    """Handle SelfTransferException by returning a 400 JSON response.
    
    Args:
        request (Request): The FastAPI request object
        exc (SelfTransferException): The exception instance that was raised
        
    Returns:
        JSONResponse: A response with status 'failure' and appropriate message, status code 400
    """
    return JSONResponse(
        content={"status":"failure", "msg": "Transfer cannot be completed. Cannot transfer money to the same account"},
        status_code=400
    )