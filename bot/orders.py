"""Order management and processing"""

import logging
from typing import Dict, Any
from bot.client import BinanceFuturesClient

logger = logging.getLogger(__name__)

class OrderManager:
    """Manages order placement and processing"""
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize OrderManager
        
        Args:
            client: BinanceFuturesClient instance
        """
        self.client = client
    
    def place_order(self, symbol: str, side: str, order_type: str,
                   quantity: float, price: float = None) -> Dict[str, Any]:
        """
        Place an order and format response for display
        
        Returns:
            Formatted order response
        """
        try:
            # Get current price for market orders (for display/info)
            if order_type == 'MARKET':
                current_price = self.client.get_symbol_price(symbol)
                logger.info(f"Current market price for {symbol}: {current_price}")
            
            # Place the order
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
            
            # Format response for display
            formatted_response = {
                'orderId': response.get('orderId'),
                'symbol': response.get('symbol'),
                'side': response.get('side'),
                'type': response.get('type'),
                'status': response.get('status'),
                'origQty': response.get('origQty'),
                'executedQty': response.get('executedQty'),
                'avgPrice': response.get('avgPrice', '0'),
                'price': response.get('price', '0'),
                'time': response.get('updateTime', response.get('transactTime'))
            }
            
            return {
                'success': True,
                'order': formatted_response,
                'message': f"Order {response.get('orderId')} placed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Order failed: {str(e)}"
            }