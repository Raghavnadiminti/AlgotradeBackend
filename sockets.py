import asyncio 
from server import manager


def send_signal(signal_data: dict):
    # This can be called from anywhere in your code
    asyncio.create_task(manager.broadcast(signal_data))