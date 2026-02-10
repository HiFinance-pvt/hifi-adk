from typing import Dict, Any
import json
from dotenv import load_dotenv
from google.adk.tools.tool_context import ToolContext
import logging
from google.cloud import firestore
from ..core import Kite, get_firestore_client
from ..schema import StockActionSchema

load_dotenv()

logger = logging.getLogger(__name__)

def get_zerodha_login_url(tool_context: ToolContext) -> str:
    """
    Get the Zerodha login URL for user authentication.
    First checks if user is already authenticated.
    Returns the URL where user needs to login to get request token if not authenticated.
    """
    user_id = tool_context.state.get('user_id')
    
    # Check if user_id exists
    if user_id:
        try:
            # Check Firestore for existing integration
            zerodha_doc_ref = get_firestore_client().collection("users").document(user_id).collection("integrations").document("zerodha")
            zerodha_doc = zerodha_doc_ref.get()
            
            if zerodha_doc.exists:
                zerodha_data = zerodha_doc.to_dict()
                integration_status = zerodha_data.get("status")
                access_token = zerodha_data.get("accessToken")
                
                # If already connected with valid token, inform user
                if integration_status == "connected" and access_token:
                    logger.info(f"User {user_id} already has active Zerodha integration")
                    return "You are already authenticated with Zerodha. Your integration is active."
                elif integration_status in ["expired", "error"]:
                    logger.info(f"User {user_id} has {integration_status} Zerodha integration, providing new login URL")
        except Exception as e:
            logger.warning(f"Error checking existing integration: {str(e)}")
    
    # Generate and return login URL if not authenticated or check failed
    login_url = Kite().generate_login_url()
    return f"Please visit this URL to authenticate with Zerodha: {login_url}"

def check_kite_auth(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Check if the user is authenticated with Zerodha.
    If authenticated, returns user details and access token.
    If not authenticated, checks Firestore for access token.
    
    Args:
        tool_context: The context containing user state and session data.

    Returns:
        A dictionary containing the authentication status and user details if authenticated.
    """
    user_id = tool_context.state.get('user_id')
    access_token = tool_context.state.get("kite_access_token")

    # Validate user_id exists
    if not user_id:
        logger.error("User ID not found in tool_context state")
        return {
            "message": "User ID not found. Please ensure you are logged in.",
            "status": "error"
        }

    logger.info(f"Checking authentication for user: {user_id}")
    # Don't print access tokens for security reasons

    # If access token exists in state, return authenticated
    if access_token:
        return {
            "message": "You are authenticated with Zerodha.",
            "user_id": user_id,
            "access_token": access_token,
            "kite_authenticated": True,
            "status": "authenticated"
        }

    # Try to fetch from Firestore
    try:
        # New Firestore path: users/{userId}/integrations/zerodha
        zerodha_doc_ref = get_firestore_client().collection("users").document(user_id).collection("integrations").document("zerodha")
        zerodha_doc = zerodha_doc_ref.get()
        
        if not zerodha_doc.exists:
            logger.warning(f"Zerodha integration not found in Firestore for user_id: {user_id}")
            return {
                "message": "You are not authenticated with Zerodha. Please login first.",
                "status": "unauthenticated"
            }
        
        zerodha_data = zerodha_doc.to_dict()
        integration_status = zerodha_data.get("status")
        access_token = zerodha_data.get("accessToken")
        
        # Check integration status
        if integration_status not in ["connected"]:
            logger.warning(f"Zerodha integration status is '{integration_status}' for user_id: {user_id}")
            return {
                "message": f"Zerodha integration is {integration_status}. Please reconnect.",
                "status": integration_status
            }
        
        if not access_token:
            logger.warning(f"Access token not found in Firestore for user_id: {user_id}")
            return {
                "message": "You are not authenticated with Zerodha. Please login first.",
                "status": "unauthenticated"
            }
        
        # Update state with fetched access token
        logger.info(f"Access token retrieved from Firestore for user: {user_id}")
        tool_context.state["kite_access_token"] = access_token
        tool_context.state["kite_authenticated"] = True
        
        # Update lastVerifiedAt timestamp
        zerodha_doc_ref.update({"lastVerifiedAt": firestore.SERVER_TIMESTAMP})
        
        return {
            "message": "You are authenticated with Zerodha.",
            "user_id": user_id,
            "access_token": access_token,
            "kite_authenticated": True,
            "status": "authenticated",
            "integration_status": integration_status
        }
        
    except Exception as e:
        logger.error(f"Failed to get access token from Firestore: {str(e)}", exc_info=True)
        return {
            "message": "Failed to verify authentication. Please try logging in again.",
            "status": "error",
            "error": str(e)
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
        if not tool_context.state.get("kite_access_token"):
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
