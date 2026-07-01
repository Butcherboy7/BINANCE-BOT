"""
Low-level client wrapper for the Binance Futures Testnet API.
Handles requests, HMAC-SHA256 signature generation, headers, and retry logic.
"""
import logging
import urllib.parse
import time
import requests
from requests.exceptions import RequestException

from bot.config import Config
from bot.exceptions import NetworkError, BinanceAPIError
from bot.models import OrderRequest, OrderResponse
from bot.utils import generate_signature, get_timestamp, get_headers
from bot.logging_config import setup_logger

logger = setup_logger("binance_client")

class BinanceClient:
    """Handles REST communications with Binance Futures Testnet."""
    
    def __init__(self, api_key: str = None, secret_key: str = None, base_url: str = None):
        self.api_key = api_key or Config.API_KEY
        self.secret_key = secret_key or Config.SECRET_KEY
        self.base_url = (base_url or Config.BASE_URL).rstrip("/")
        
    def _send_signed_request(self, method: str, path: str, params: dict) -> dict:
        """
        Sends an authenticated, signed request to the Binance API with retry logic.
        
        Args:
            method (str): HTTP method (e.g., 'POST', 'GET').
            path (str): Endpoint path (e.g., '/fapi/v1/order').
            params (dict): Request parameters.
            
        Returns:
            dict: The parsed JSON response.
        """
        url = f"{self.base_url}{path}"
        
        # Inject standard recvWindow and current timestamp
        params = params.copy()
        params["recvWindow"] = 60000  # Generous window to mitigate local clock sync issues
        params["timestamp"] = get_timestamp()
        
        # Build query string and generate cryptographic HMAC-SHA256 signature
        query_string = urllib.parse.urlencode(params)
        signature = generate_signature(self.secret_key, query_string)
        query_string += f"&signature={signature}"
        
        headers = get_headers(self.api_key)
        
        # Log request (hiding sensitive keys/signatures is good practice, but log details)
        logger.info(f"API Request - Method: {method} | URL: {url} | Params: {query_string}")
        
        max_retries = 3
        backoff = 1.0  # seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                if method.upper() == "POST":
                    response = requests.post(url, data=query_string, headers=headers, timeout=10)
                else:
                    response = requests.get(url, params=query_string, headers=headers, timeout=10)
                
                # Check for API-specific errors (status code >= 400)
                if response.status_code >= 400:
                    try:
                        error_json = response.json()
                        error_code = error_json.get("code", 0)
                        error_msg = error_json.get("msg", "Unknown API error")
                    except Exception:
                        error_code = -1
                        error_msg = response.text or "Could not parse error response"
                        
                    logger.error(
                        f"API Error Response - Status: {response.status_code} | "
                        f"Code: {error_code} | Msg: {error_msg}"
                    )
                    raise BinanceAPIError(
                        code=error_code,
                        message=error_msg,
                        status_code=response.status_code
                    )
                    
                response_json = response.json()
                logger.info(f"API Response - Status: {response.status_code} | Payload: {response_json}")
                return response_json
                
            except RequestException as e:
                logger.warning(
                    f"Network attempt {attempt}/{max_retries} failed for {method} {path}. "
                    f"Error: {e}"
                )
                if attempt == max_retries:
                    logger.critical(f"All network attempts failed. Last exception: {e}")
                    raise NetworkError(f"Network request failed: {e}")
                
                # Exponential backoff
                time.sleep(backoff)
                backoff *= 2
                
        raise NetworkError("Unexpected loop termination in request handling.")

    def place_order(self, order: OrderRequest) -> OrderResponse:
        """
        Sends the order request to Binance Futures Testnet and maps the response.
        
        Args:
            order (OrderRequest): The order parameters.
            
        Returns:
            OrderResponse: Standardized response dataclass.
        """
        path = "/fapi/v1/order"
        
        # Prepare parameters
        params = {
            "symbol": order.symbol,
            "side": order.side,
            "type": order.order_type,
            "quantity": order.quantity,
        }
        
        # If LIMIT order, price and timeInForce are mandatory
        if order.order_type == "LIMIT":
            params["price"] = order.price
            params["timeInForce"] = "GTC"  # Good Till Cancel is standard default
            
        # Send post request
        res_data = self._send_signed_request("POST", path, params)
        
        # Extract variables from Binance response
        # Note: avgPrice is calculated from executedQty and cumQuote/cumQty or from avgPrice field
        # Binance Futures returns "avgPrice" field in response payload
        avg_price = float(res_data.get("avgPrice", 0.0))
        if avg_price == 0.0:
            # Fallback if price is returned
            avg_price = float(res_data.get("price", 0.0))
            
        return OrderResponse(
            order_id=str(res_data.get("orderId")),
            symbol=res_data.get("symbol"),
            status=res_data.get("status"),
            side=res_data.get("side"),
            order_type=res_data.get("type"),
            executed_qty=float(res_data.get("executedQty", 0.0)),
            avg_price=avg_price,
            client_order_id=res_data.get("clientOrderId"),
            raw_response=res_data
        )
