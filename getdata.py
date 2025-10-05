
import yfinance as yf
import pandas as pd
from configs.dbconfig import engine 
from postdb import get_from_db_n

from postdb import post_in_db


def get_stock_data(ticker, period="2y", interval="1d"):
    """
    Get historical price data and latest price for the specified ticker.

    Parameters:
        ticker (str): Stock symbol (e.g., "AAPL")
        period (str): Period for historical data (e.g., "1y", "1mo", "max")
        interval (str): Data granularity ("1d", "1m", etc.)

    Returns:
        historical (pd.DataFrame): Historical OHLCV data
        last_quote (float): Latest price ('Close' from most recent row)
    """
    stock = yf.Ticker(ticker)
    historical = stock.history(period=period, interval=interval)

    last_quote = None
    if not historical.empty:
        last_quote = historical['Close'][-1]    # Most recent close (acts as quasi-live price)
    return historical, last_quote

# Example Usage:
# historical_data, latest_price = get_stock_data("AAPL", period="1mo", interval="1m")




