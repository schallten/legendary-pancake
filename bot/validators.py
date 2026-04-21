"""Input validation for trading operations"""

import re
from typing import Dict, Any
from decimal import Decimal, InvalidOperation

def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format"""
    pattern = r'^[A-Z]{3,6}[A-Z]{3,6}$'  # e.g., BTCUSDT, ETHUSDT
    return bool(re.match(pattern, symbol))

def validate_side(side: str) -> bool:
    """Validate order side"""
    return side.upper() in ['BUY', 'SELL']

def validate_order_type(order_type: str) -> bool:
    """Validate order type"""
    return order_type.upper() in ['MARKET', 'LIMIT']

def validate_quantity(quantity: str) -> tuple[bool, float]:
    """Validate and convert quantity"""
    try:
        qty = float(quantity)
        if qty <= 0:
            return False, 0
        if qty > 1000:  # Reasonable upper limit for testnet
            return False, 0
        return True, qty
    except (ValueError, TypeError):
        return False, 0

def validate_price(price: str, order_type: str) -> tuple[bool, float]:
    """Validate price for limit orders"""
    if order_type.upper() == 'MARKET':
        return True, 0.0
    
    try:
        price_val = float(price)
        if price_val <= 0:
            return False, 0
        return True, price_val
    except (ValueError, TypeError):
        return False, 0

def validate_order_params(symbol: str, side: str, order_type: str, 
                         quantity: str, price: str = None) -> Dict[str, Any]:
    """
    Validate all order parameters
    Returns: dict with 'valid' flag, 'errors' list, and validated values
    """
    errors = []
    validated = {}
    
    # Validate symbol
    if not validate_symbol(symbol):
        errors.append(f"Invalid symbol: {symbol}. Must be like 'BTCUSDT'")
    else:
        validated['symbol'] = symbol.upper()
    
    # Validate side
    if not validate_side(side):
        errors.append(f"Invalid side: {side}. Must be BUY or SELL")
    else:
        validated['side'] = side.upper()
    
    # Validate order type
    if not validate_order_type(order_type):
        errors.append(f"Invalid order type: {order_type}. Must be MARKET or LIMIT")
    else:
        validated['type'] = order_type.upper()
    
    # Validate quantity
    valid_qty, qty_val = validate_quantity(quantity)
    if not valid_qty:
        errors.append(f"Invalid quantity: {quantity}. Must be positive number <= 1000")
    else:
        validated['quantity'] = qty_val
    
    # Validate price for limit orders
    if order_type.upper() == 'LIMIT':
        if not price:
            errors.append("Price is required for LIMIT orders")
        else:
            valid_price, price_val = validate_price(price, order_type)
            if not valid_price:
                errors.append(f"Invalid price: {price}. Must be positive number")
            else:
                validated['price'] = price_val
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'validated': validated
    }