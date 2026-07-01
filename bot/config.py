"""
Configuration loader and validator for the Binance Futures Trading Bot.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from bot.exceptions import ValidationError

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Holds configuration settings loaded from environment variables."""
    
    API_KEY = os.getenv("BINANCE_API_KEY")
    SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    BASE_URL = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com").rstrip("/")
    
    @classmethod
    def validate(cls, dry_run: bool = False) -> None:
        """
        Validates that required configuration is present.
        
        Args:
            dry_run (bool): If True, warnings are issued instead of exceptions.
        """
        if dry_run:
            # For dry-runs, we don't require valid credentials
            return
            
        if not cls.API_KEY or cls.API_KEY.strip() == "your_api_key_here":
            raise ValidationError(
                "BINANCE_API_KEY is missing or set to the default placeholder. "
                "Please configure your key in the .env file."
            )
            
        if not cls.SECRET_KEY or cls.SECRET_KEY.strip() == "your_api_secret_here":
            raise ValidationError(
                "BINANCE_SECRET_KEY is missing or set to the default placeholder. "
                "Please configure your secret key in the .env file."
            )
            
        if not cls.BASE_URL.startswith("https://"):
            raise ValidationError(
                f"BINANCE_BASE_URL must be a secure HTTPS url. Current value: {cls.BASE_URL}"
            )
