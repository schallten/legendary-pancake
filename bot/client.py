"""Binance Futures API Client"""

import httpx
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import hashlib
import hmac
import time

logger = logging.getLogger(__name__)

class BinanceFuturesClient:
    """Binance Futures Testnet API Client"""
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize the Binance Futures client
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = httpx.Client(timeout=30.0)
        
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _send_request(self, method: str, endpoint: str, 
                     params: Optional[Dict] = None, 
                     signed: bool = False) -> Dict[str, Any]:
        """
        Send HTTP request to Binance API
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether request requires signature
            
        Returns:
            Response JSON as dict
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        if signed:
            if params is None:
                params = {}
            params['timestamp'] = int(time.time() * 1000)
            params['recvWindow'] = 5000
            params['signature'] = self._generate_signature(params)
        
        logger.debug(f"Request: {method} {url}")
        logger.debug(f"Params: {params}")
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return self._send_request('GET', '/fapi/v2/account', signed=True)
    
    def get_symbol_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        response = self._send_request('GET', '/fapi/v1/ticker/price', 
                                     params={'symbol': symbol})
        return float(response['price'])
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place an order on Binance Futures
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            order_type: 'MARKET' or 'LIMIT'
            quantity: Order quantity
            price: Price for limit orders
            
        Returns:
            Order response from Binance
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        
        if order_type == 'LIMIT':
            params['price'] = price
            params['timeInForce'] = 'GTC'  # Good Till Cancelled
        
        logger.info(f"Placing {order_type} {side} order for {quantity} {symbol}")
        if price:
            logger.info(f"Limit price: {price}")
        
        response = self._send_request('POST', '/fapi/v1/order', 
                                     params=params, signed=True)
        
        logger.info(f"Order placed successfully. Order ID: {response.get('orderId')}")
        return response
    
    def close(self):
        """Close the HTTP client session"""
        self.session.close()