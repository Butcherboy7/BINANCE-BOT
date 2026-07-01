"""
Dataclasses representing structured request and response models.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class OrderRequest:
    """Represents the structured parameters of an order request."""
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    dry_run: bool = False


@dataclass(frozen=True)
class OrderResponse:
    """Represents a clean, standardized order execution response."""
    order_id: str
    symbol: str
    status: str
    side: str
    order_type: str
    executed_qty: float
    avg_price: float
    client_order_id: Optional[str] = None
    raw_response: Optional[dict] = None
