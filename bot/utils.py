"""
Helper utilities for cryptographic signatures, timestamp generation, and headers.
"""
import hmac
import hashlib
import time

def generate_signature(secret_key: str, query_string: str) -> str:
    """
    Generates an HMAC-SHA256 signature for the given query string.
    
    Args:
        secret_key (str): Secret key to sign with.
        query_string (str): The payload query string to sign.
        
    Returns:
        str: Hexadecimal signature string.
    """
    return hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def get_timestamp() -> int:
    """
    Returns the current UNIX timestamp in milliseconds.
    
    Returns:
        int: Millisecond timestamp.
    """
    return int(time.time() * 1000)

def get_headers(api_key: str) -> dict:
    """
    Generates the headers required for Binance authenticated endpoints.
    
    Args:
        api_key (str): The API key header.
        
    Returns:
        dict: Headers dictionary.
    """
    return {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-MBX-APIKEY": api_key
    }
