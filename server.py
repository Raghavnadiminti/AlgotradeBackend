# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect,JSONResponse,HTTPException,Depends
from pydantic import BaseModel
import uvicorn
from paertrading import LivePaperTrader 
from getdata import get_stock_data
from MAC import moving_average_strategy,backtesting 
from postdb import post_in_db
from MAC import livedata
from models.datamodel import Stocks
from configs.dbconfig import get_db
import asyncio

app = FastAPI(title="My FastAPI App")
from sqlalchemy.orm import Session
# Example data model
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

# Root endpoint
@app.get("/")
def read_root():
    return 

# Example POST endpoint
@app.post("/items/")
def create_item(item: Item):
    return {"item": item}

@app.get("/stocks/{stock_name}")
def get_stocks(stock_name: str, db: Session = Depends(get_db)):
    stocks = db.query(Stocks).filter(Stocks.stock_name == stock_name).all()
    if not stocks:
        raise HTTPException(status_code=404, detail="No stocks found")
    
    # Convert all records to list of dicts
    stock_data = []
    for stock in stocks:
        stock_data.append({
            "id": stock.id,
            "stock_name": stock.stock_name,
            "date": stock.date.isoformat(),
            "open": stock.open,
            "high": stock.high,
            "low": stock.low,
            "close": stock.close,
            "volume": stock.volume
        })
    return JSONResponse(content=stock_data)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # just keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)










# Run with Uvicorn when executed directly
if __name__ == "__main__":

     

    historic_data,_=get_stock_data("BTC-USD") 
    mdf=moving_average_strategy(historic_data) 
    bdf=backtesting(mdf)
    post_in_db(bdf,"BTC-USD")
    asyncio.run(livedata()) 
    



    




    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
