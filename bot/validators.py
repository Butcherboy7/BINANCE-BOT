"""
Input validators for CLI arguments and request parameters.
"""
from typing import Optional
from bot.exceptions import ValidationError

def validate_symbol(symbol: str) -> str:
    """Validates the trading symbol format."""
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Trading symbol cannot be empty.")
    
    clean_symbol = symbol.strip().upper()
    
    # Basic sanity checks for Binance symbol formatting
    if not clean_symbol.isalnum():
        raise ValidationError(f"Invalid symbol '{symbol}': Symbols must be alphanumeric (e.g., BTCUSDT).")
        
    return clean_symbol

def validate_side(side: str) -> str:
    """Validates the order side."""
    if not side or not isinstance(side, str):
        raise ValidationError("Order side cannot be empty.")
        
    clean_side = side.strip().upper()
    valid_sides = {"BUY", "SELL"}
    if clean_side not in valid_sides:
        raise ValidationError(f"Invalid side '{side}': Must be either BUY or SELL.")
        
    return clean_side

def validate_type(order_type: str) -> str:
    """Validates the order type."""
    if not order_type or not isinstance(order_type, str):
        raise ValidationError("Order type cannot be empty.")
        
    clean_type = order_type.strip().upper()
    valid_types = {"MARKET", "LIMIT"}
    if clean_type not in valid_types:
        raise ValidationError(f"Invalid order type '{order_type}': Must be either MARKET or LIMIT.")
        
    return clean_type

def validate_quantity(quantity: float) -> float:
    """Validates the order quantity."""
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity '{quantity}' must be a valid float value.")
        
    if qty <= 0:
        raise ValidationError(f"Quantity '{qty}' must be greater than zero.")
        
    return qty

def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """Validates the order price based on the order type."""
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required when order type is LIMIT.")
        try:
            val = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price '{price}' must be a valid float value.")
            
        if val <= 0:
            raise ValidationError(f"Price '{val}' must be greater than zero for LIMIT orders.")
        return val
    else:
        if price is not None:
            # We can log a warning or raise an exception. Let's raise an exception to keep user inputs strict
            raise ValidationError("Price should not be specified for MARKET orders.")
        return None

def validate_all(symbol: str, side: str, order_type: str, quantity: float, price: Optional[float]) -> tuple[str, str, str, float, Optional[float]]:
    """
    Runs all validators in sequence and returns the sanitized values.
    Raises ValidationError on the first failure.
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_type(order_type)
    clean_qty = validate_quantity(quantity)
    clean_price = validate_price(price, clean_type)
    
    return clean_symbol, clean_side, clean_type, clean_qty, clean_price
