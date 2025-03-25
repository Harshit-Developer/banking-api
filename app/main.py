from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import banking
from app.database.db import Database
import logging
from dotenv import load_dotenv
import os

from app.services.banking import BankingService
from app.utils.exception_handler import AccountNotFoundExceptionHandler, CustomerNotFoundExceptionHandler, InsufficientFundsExceptionHandler, SelfTransferExceptionHandler
from app.utils.exceptions import AccountNotFoundException, CustomerNotFoundException, InsufficientFundsException, SelfTransferException

load_dotenv()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events using FastAPI's lifespan context manager."""
    logger.info("Starting up Banking API")  # Runs on startup
    yield 
    logger.info("Shutting down Banking API")  # Runs on shutdown

app = FastAPI(title="Banking API", version="1.0.0", description="Internal API for banking operations", lifespan=lifespan)


app.state.db = Database()
app.state.banking_service = BankingService(app.state.db)

app.add_exception_handler(AccountNotFoundException,AccountNotFoundExceptionHandler)
app.add_exception_handler(CustomerNotFoundException,CustomerNotFoundExceptionHandler)
app.add_exception_handler(InsufficientFundsException,InsufficientFundsExceptionHandler)
app.add_exception_handler(SelfTransferException,SelfTransferExceptionHandler)


app.include_router(banking.router)

