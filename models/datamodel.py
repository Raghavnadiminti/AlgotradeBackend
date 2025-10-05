from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base
from configs.dbconfig import Base

class Stocks(Base):
    __tablename__ = "stock_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    sma_short = Column(Float)
    sma_long = Column(Float)
    signal = Column(Integer)     # Buy(1), Sell(-1), Hold(0)
    position = Column(Integer)   # Shares held
    portfolio = Column(Float)    # Total portfolio value at this step
    pnl = Column(Float)          # Profit/loss at this step
    return_percent = Column(Float)  # Return percentage at this step

    __table_args__ = (
        UniqueConstraint('stock_name', 'date', name='unique_stock_date'),
    )

