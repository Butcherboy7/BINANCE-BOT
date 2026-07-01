"""
Business logic layer for coordinating order placements.
Deals with validation, dry-run simulations, and client execution.
"""
from typing import Optional
from bot.config import Config
from bot.validators import validate_all
from bot.models import OrderRequest, OrderResponse
from bot.binance_client import BinanceClient
from bot.logging_config import setup_logger

logger = setup_logger("orders")

def execute_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    dry_run: bool = False
) -> OrderResponse:
    """
    Coordinates validation, dry-run mode checks, client dispatch, and response formatting.
    
    Args:
        symbol (str): Trading pair symbol (e.g. BTCUSDT)
        side (str): BUY or SELL
        order_type (str): MARKET or LIMIT
        quantity (float): Quantity to transact
        price (Optional[float]): Required for LIMIT orders
        dry_run (bool): If True, validates parameters but does not hit the live API.
        
    Returns:
        OrderResponse: Dataclass containing details of execution.
    """
    # 1. Validate inputs locally
    clean_symbol, clean_side, clean_type, clean_qty, clean_price = validate_all(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price
    )
    
    # 2. Check configuration (Only validate keys if not a dry-run)
    Config.validate(dry_run=dry_run)
    
    # Create request object
    order_req = OrderRequest(
        symbol=clean_symbol,
        side=clean_side,
        order_type=clean_type,
        quantity=clean_qty,
        price=clean_price,
        dry_run=dry_run
    )
    
    logger.info(
        f"Order placement initiated - Symbol: {order_req.symbol} | "
        f"Side: {order_req.side} | Type: {order_req.order_type} | Qty: {order_req.quantity} | "
        f"Price: {order_req.price} | Dry Run: {order_req.dry_run}"
    )
    
    # 3. Handle Dry Run Simulation
    if dry_run:
        logger.info("Dry-run mode is enabled. Skipping actual API request.")
        simulated_response = OrderResponse(
            order_id="DRY_RUN_ID_999",
            symbol=order_req.symbol,
            status="FILLED" if order_req.order_type == "MARKET" else "NEW",
            side=order_req.side,
            order_type=order_req.order_type,
            executed_qty=order_req.quantity if order_req.order_type == "MARKET" else 0.0,
            avg_price=order_req.price if order_req.price else 95000.0,  # Mock price for BTC or similar
            client_order_id="dry_run_client_id_123",
            raw_response={"dry_run": True, "message": "Simulated local validation passed successfully"}
        )
        return simulated_response
        
    # 4. Live API Placement
    client = BinanceClient()
    response = client.place_order(order_req)
    
    return response
