import os

from dotenv import load_dotenv
from kiteconnect import KiteConnect

from ..schema import StockActionSchema

load_dotenv()


class Kite:
    def __init__(self):
        self.kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))

    def generate_login_url(self):
        """
        Generate the login URL for Zerodha authentication.
        Returns the URL where user needs to login to get request token.
        """
        return self.kite.login_url()
    

    def __set_access_token(self, access_token: str):
        """
        Set the access token for authenticated requests.
        """
        self.kite.set_access_token(access_token)
        return True
    
    def get_holdings(self, access_token: str):
        """
        Get the user's current holdings/portfolio.
        Returns a list of holdings with details like quantity, last price, etc.
        """
        self.__set_access_token(access_token=access_token)
        holdings = self.kite.holdings()
        return holdings
    
    def stock_action(self, order_schema: StockActionSchema, access_token: str):
        """
        Execute a stock action (buy/sell) for the given symbol and quantity.
        Args:
            order_schema (StockActionSchema): Order details including action, symbol, quantity, etc.
            access_token (str): Access token for authentication
        Returns:
            Order response from Zerodha API.
        """
        self.__set_access_token(access_token=access_token)
        if order_schema.action not in ["buy", "sell"]:
            raise ValueError("Action must be 'buy' or 'sell'")
        
        order_params = {
            "tradingsymbol": order_schema.symbol,
            "quantity": order_schema.quantity,
            "transaction_type": order_schema.action.upper(),
            "order_type": order_schema.order_type,
            "product": order_schema.product,
            "exchange": order_schema.exchange
        }
        
        return self.kite.place_order(**order_params)
    
    def get_order_history(self, access_token: str):
        """
        Get the order history for the user.
        Args:
            access_token (str): Access token for authentication
        Returns:
            List of orders with details like order ID, status, etc.
        """
        self.__set_access_token(access_token=access_token)
        return self.kite.orders()
    
    def get_user_profile(self, access_token: str):
        """
        Get the user's profile information.
        Args:
            access_token (str): Access token for authentication
        Returns:
            User profile details including name, email, etc.
        """
        self.__set_access_token(access_token=access_token)
        return self.kite.profile()