from models.datamodel import Stocks 
# from configs.dbconfig import engine
from sqlalchemy import create_engine
from sqlalchemy import text 
engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/postgres") 
import pandas as pd
def post_in_db(df,stock):

    df = df.reset_index().rename(columns={"index": "date"})
    
    # Add stock name column
    df["stock_name"] = stock

    # Reorder columns to match table schema
    df = df[[
        "stock_name", "Date", "Open", "High", "Low", "Close", "Volume",
        "shrt50", "long200", "Signal", "Position", "Portfolio"
    ]]

    # Convert column names to lowercase to match SQLAlchemy class
    df.columns = [c.lower() for c in df.columns]
    df.to_sql("stock_signals", engine, if_exists="append", index=False)


def get_from_db_n(stock,n=200):
    query = text("""
        SELECT *
        FROM stock_signals
        WHERE stock_name = :symbol
        ORDER BY date DESC
        LIMIT :limit
    """)
    df = pd.read_sql(query, engine, params={"symbol": stock, "limit": n})
    df = df[[
        "stock_name", "date", "open", "high", "low", "close", "volume",
        "shrt50", "long200", "signal", "position", "portfolio"
    ]]

    # Convert column names to lowercase to match SQLAlchemy class
    df.columns = [c.capitalize() for c in df.columns]
    return df.iloc[::-1]