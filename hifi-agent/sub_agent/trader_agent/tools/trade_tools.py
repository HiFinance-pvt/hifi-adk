from typing import Dict, Any
import json

from dotenv import load_dotenv
from google.adk.tools.tool_context import ToolContext
import logging

from ..core import Kite, client
from ..schema import StockActionSchema


load_dotenv()

logger = logging.getLogger(__name__)

def get_zerodha_login_url(tool_context: ToolContext) -> str:
    """
    Get the Zerodha login URL for user authentication.
    Returns the URL where user needs to login to get request token.
    """
    
    login_url = Kite().generate_login_url()
    
    # Store in session for later use
    tool_context.state["kite_authenticated"] = False

    return f"Please visit this URL to authenticate with Zerodha: {login_url}"

def check_kite_auth(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Check if the user is authenticated with Zerodha.
    If authenticated, returns user details and access token.
    If not authenticated, checks Firestore for access token.
    
    Args:
        tool_context: The context containing user state and session data.

    Raises:
        ValueError: If user_id or kite_access_token is not found in tool_context state.

    Returns:
        A dictionary containing the authentication status and user details if authenticated.
    """
    user_id = tool_context.state.get("user_id")
    access_token = tool_context.state.get("kite_access_token")

    if access_token:
        return {
            "message": "You are authenticated with Zerodha.",
            "user_id": tool_context.state.get("kite_user_id"),
            "access_token": tool_context.state.get("kite_access_token"),
            "kite_authenticated": tool_context.state.get("kite_authenticated", True),
            "status": "authenticated"
        }

    else:
        # access_token = client.document("users").collection(user_id).get().to_dict().get("kite_access_token")
        access_token = "1ieOtV24XszOP1TM4qeeUHAafGYDufDF"

        if access_token:
            tool_context.state["kite_access_token"] = access_token
            tool_context.state["kite_authenticated"] = True
            return {
                "message": "You are authenticated with Zerodha.",
                "user_id": tool_context.state.get("kite_user_id"),
                "access_token": tool_context.state.get("kite_access_token"),
                "status": "authenticated"
            }

        else:
            return {
                "message": "You are not authenticated with Zerodha. Please login first.",
                "status": "unauthenticated"
            }

def buy_stock(
    symbol: str,
    quantity: int,
    tool_context: ToolContext,
    exchange: str = "BSE",
    order_type: str = "LIMIT"
) -> Dict[str, Any]:
    """
    Place a buy order for stocks.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE", "TCS")
        quantity: Number of shares to buy
        price: Price per share (for LIMIT orders)
        order_type: Order type - "LIMIT" or "MARKET"
        exchange: Exchange - "NSE" or "BSE"
    """
    try:
       # Check if user is authenticated
        if not tool_context.state.get("kite_authenticated") or not tool_context.state.get("kite_access_token"):
            return {"error": "Please authenticate with Zerodha first using get_zerodha_login_url"}
        
        order_params = {
            "action": "BUY",
            "tradingsymbol": symbol,
            "exchange": exchange,  # Default to NSE, can be made configurable
            "quantity": quantity,
            "order_type": order_type,
            "product": "CNC",  # Cash and Carry
        }

        order_schema = StockActionSchema(**order_params)
        kite = Kite().stock_action(order_schema=order_schema, access_token=tool_context.state.get("kite_access_token"))
        order_id = kite.place_order(**order_params)
        
        return {
            "message": f"Buy order placed successfully! Order ID: {order_id}, Symbol: {symbol}, Quantity: {quantity}",
            "order_id": order_id,
            "symbol": symbol,
            "quantity": quantity,
            "order_type": order_type,
            "transaction_type": "BUY"
        }
        
    except Exception as e:
        logger.error(f"Failed to place buy order: {str(e)}")
        return {"error": f"Failed to place buy order: {str(e)}"}

def sell_stock(
        symbol: str,
        quantity: int,
        tool_context: ToolContext,
        exchange: str = "BSE",
        order_type: str = "LIMIT"
        ) -> Dict[str, Any]:
    """
    Place a sell order for stocks.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE", "TCS")
        quantity: Number of shares to sell
        price: Price per share (for LIMIT orders)
        order_type: Order type - "LIMIT" or "MARKET"
    """
    try:
        # Check if user is authenticated
        # if not tool_context.state.get("zerodha_authenticated") or not tool_context.state.get("zerodha_access_token"):
        #     return {"error": "Please authenticate with Zerodha first using get_zerodha_login_url"}
        
        
        order_params = {
            "tradingsymbol": symbol,
            "exchange": exchange,
            "transaction_type": "SELL",
            "quantity": quantity,
            "order_type": order_type,
            "product": "CNC",  # Cash and Carry
        }
  
        order_id = Kite().stock_action(
            order_schema=StockActionSchema(**order_params),
            access_token=tool_context.state.get("kite_access_token")
        )
        
        return {
            "message": f"Sell order placed successfully! Order ID: {order_id}, Symbol: {symbol}, Quantity: {quantity}",
            "order_id": order_id,
            "symbol": symbol,
            "quantity": quantity,
            "order_type": order_type,
            "transaction_type": "SELL"
        }
        
    except Exception as e:
        logger.error(f"Failed to place sell order: {str(e)}")
        return {"error": f"Failed to place sell order: {str(e)}"}

def get_portfolio(tool_context: ToolContext) -> Dict[str, Any]:
    """Get user's current portfolio/holdings."""
    try:
        # if not tool_context.state.get("zerodha_authenticated"):
        #     return {"error": "Please authenticate with Zerodha first using get_zerodha_login_url"}

        holdings = Kite().get_holdings(access_token=tool_context.state.get("kite_access_token"))

        if not holdings:
            return {
                "message": "No holdings found in your portfolio.",
                "holdings": []
            }
        
        portfolio_data = []
        total_value = 0
        
        for holding in holdings:
            # Skip if holding is not a dictionary
            if not isinstance(holding, dict):
                continue
                
            current_value = holding['last_price'] * holding['quantity']
            total_value += current_value
            
            portfolio_data.append({
                "symbol": holding['tradingsymbol'],
                "quantity": holding['quantity'],
                "last_price": holding['last_price'],
                "current_value": current_value,
                "pnl": holding.get('pnl', 0),
                "average_price": holding.get('average_price', 0),
                "day_change": holding.get('day_change', 0),
                "day_change_percentage": holding.get('day_change_percentage', 0)
            })
        
        portfolio_str = "Your Portfolio:\n"
        for item in portfolio_data:
            portfolio_str += f"- {item['symbol']}: {item['quantity']} shares, Current Value: ₹{item['current_value']:.2f}\n"
        
        return {
            "message": portfolio_str,
            "holdings": portfolio_data,
            "total_value": total_value
        }
        
    except Exception as e:
        logger.error(f"Failed to get portfolio: {str(e)}")
        return {"error": f"Failed to get portfolio: {str(e)}"}

def get_order_status(order_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Get status of a specific order."""
    try:
        if not tool_context.state.get("zerodha_authenticated"):
            return {"error": "Please authenticate with Zerodha first using get_zerodha_login_url"}
        
        orders = Kite().get_order_history(access_token=tool_context.state.get("kite_access_token"))
        
        for order in orders:
            if order['order_id'] == order_id:
                return {
                    "message": f"Order {order_id}: {order['status']} - {order['tradingsymbol']} {order['transaction_type']} {order['quantity']} @ {order.get('price', 'Market')}",
                    "order_id": order_id,
                    "status": order['status'],
                    "symbol": order['tradingsymbol'],
                    "transaction_type": order['transaction_type'],
                    "quantity": order['quantity'],
                    "price": order.get('price', 'Market')
                }
        
        return {"error": f"Order {order_id} not found."}
        
    except Exception as e:
        logger.error(f"Failed to get order status: {str(e)}")
        return {"error": f"Failed to get order status: {str(e)}"}

def get_user_profile(tool_context: ToolContext) -> Dict[str, Any]:
    """Get user's profile information."""
    try:
        if not tool_context.state.get("zerodha_authenticated"):
            return {"error": "Please authenticate with Zerodha first using get_zerodha_login_url"}
        user_profile_bytes = Kite().get_user_profile(access_token=tool_context.state.get("kite_access_token"))
        user_profile = json.loads(user_profile_bytes.decode('utf-8'))

        return {
            "message": "User profile retrieved successfully.",
            "user_name": user_profile.get("user_name"),
            "email": user_profile.get("email"),
            "broker": user_profile.get("broker"),
            "exchange": user_profile.get("exchange"),
            "product": user_profile.get("product"),
        }
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {str(e)}")
        return {"error": f"Failed to get user profile: {str(e)}"}