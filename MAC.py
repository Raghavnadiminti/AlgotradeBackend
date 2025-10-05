from getdata import get_stock_data 
import pandas as pd
from postdb import post_in_db
from postdb import get_from_db_n
import asyncio 
import yfinance as yf
from sockets import send_signal

def moving_average_strategy(data):

    df=pd.DataFrame(data)
    short_window=50 
    long_window=200 
    df['shrt50']=df['Close'].rolling(window=short_window).mean() 
    df['long200']=df['Close'].rolling(window=long_window).mean() 
    df['Signal'] = 0
    df['Signal'] = 0  # initialize with zeros

# Safe assignment starting from short_window
    df.loc[df.index[short_window:], 'Signal'] = (
        df.loc[df.index[short_window:], 'shrt50'] > df.loc[df.index[short_window:], 'long200']
    ).astype(int)
    df['Position'] = df['Signal'].diff()

    return df 


def backtesting(df, initial_cash=1000000):
    cash = initial_cash
    position = 0
    df['Portfolio'] = 0.0  # total value of cash + stocks

    for idx, row in df.iterrows():
        # Buy signal
        if row['Position'] == 1:
            shares_to_buy = int(cash / row['Close'])
            if shares_to_buy > 0:
                cash -= shares_to_buy * row['Close']
                position += shares_to_buy

        # Sell signal
        elif row['Position'] == -1 and position > 0:
            cash += position * row['Close']
            position = 0

        # Portfolio value = cash + value of stock held
        df.at[idx, 'Portfolio'] = cash + position * row['Close']

    # Final calculations
    final_value = cash + position * df['Close'].iloc[-1]
    profit = final_value - initial_cash

    
    df['PnL'] = df['Portfolio'] - initial_cash
    df['Return_percent'] = (df['PnL'] / initial_cash) * 100

    return df



# data=get_stock_data("BTC-USD")
# print(data)


def live_to_historic_df(live_msg):
    """
    Convert a Yahoo live tick message to a 1-row OHLCV-style DataFrame.
    
    Parameters
    ----------
    live_msg : dict
    Returns
    -------
    pd.DataFrame
        A single-row DataFrame in standard OHLCV format:
        [DatetimeIndex, Open, High, Low, Close, Volume, Dividends, Stock Splits]
    """
    
    # Convert timestamp (Yahoo sends milliseconds)
    ts = pd.to_datetime(int(live_msg["time"]) / 1000, unit="s", utc=True).tz_convert("Asia/Kolkata")
    
    # Extract key values safely
    price = float(live_msg.get("price", None))
    open_price = float(live_msg.get("open_price", price))
    high = float(live_msg.get("day_high", price))
    low = float(live_msg.get("day_low", price))
    
    # Volume (can be total day volume or trade size)
    volume = float(live_msg.get("day_volume") or live_msg.get("last_size") or 0)
    stock=live_msg["id"]
    # Construct the row
    row = {
        "Stock_name":stock,
        "Date":ts,
        "Open": open_price,
        "High": high,
        "Low": low,
        "Close": price,
        "Volume": volume,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
    }
    
    # Create DataFrame with timestamp as index
    df = pd.DataFrame([row], index=[ts])
    df.index.name = "Datetime"
    
    return df

import asyncio






def update_df(df, new_candle):
    # Ensure both have the same columns
    new_candle = new_candle.reindex(columns=df.columns, fill_value=0)

    # Append the new candle to existing df
    df = pd.concat([df, new_candle], ignore_index=True)

    # Keep only the last 200 rows
    if len(df) > 200:
        df = df.iloc[-200:].reset_index(drop=True)

    return df



def message_handler(message):
    # print("Received message:", message)
    df=live_to_historic_df(message) 
    
    df1=get_from_db_n("BTC-USD") 
    df2=update_df(df1,df)
    print(df2)
    print(df2.columns)
    mdf=moving_average_strategy(df2) 

    bdf=backtesting(mdf)
    pdf=bdf.tail(1)
    post_in_db(pdf,"BTC-USD")
    json=pdf.to_json(orient='records')
    send_signal(json)
    print(df2)

async def livedata():
    async with yf.AsyncWebSocket() as ws:
        await ws.subscribe(["BTC-USD"])
        await ws.listen(message_handler)

