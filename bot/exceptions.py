"""
Custom exception hierarchy for the Binance Futures Trading Bot.
"""

class TradingBotError(Exception):
    """Base exception class for all trading bot related errors."""
    pass

class ValidationError(TradingBotError):
    """Raised when input validation (e.g., CLI arguments) fails."""
    pass

class NetworkError(TradingBotError):
    """Raised when network calls time out or fail after retries."""
    pass

class BinanceAPIError(TradingBotError):
    """
    Raised when the Binance API returns a non-200 status code.
    
    Attributes:
        code (int): The error code returned by Binance API.
        message (str): The error message returned by Binance API.
        status_code (int): The HTTP status code of the response.
    """
    def __init__(self, code: int, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"Binance API Error {code} ({status_code}): {message}")
