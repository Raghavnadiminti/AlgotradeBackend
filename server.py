# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from paertrading import LivePaperTrader 
from getdata import get_stock_data
from MAC import moving_average_strategy,backtesting 
from postdb import post_in_db

app = FastAPI(title="My FastAPI App")

# Example data model
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Example POST endpoint
@app.post("/items/")
def create_item(item: Item):
    return {"item": item}

# Run with Uvicorn when executed directly
if __name__ == "__main__":

     

    historic_data,_=get_stock_data("BTC-USD") 

    mdf=moving_average_strategy(historic_data) 

    bdf=backtesting(mdf)
    post_in_db(bdf,"BTC-USD")
    



    




    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
