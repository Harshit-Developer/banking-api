class BankingException(Exception):
    """Base class for all banking-related exceptions."""
    pass

class AccountNotFoundException(BankingException):
    """Exception raised when the specified account does not exist in the database."""
    pass

class CustomerNotFoundException(BankingException):
    """Exception raised when the specified customer does not exist in the database."""
    pass

class InsufficientFundsException(BankingException):
    """Exception raised when there are insufficient funds to complete a transfer."""
    pass

class SelfTransferException(BankingException):
    """Exception raised when attempting to transfer funds to the same account."""
    pass

