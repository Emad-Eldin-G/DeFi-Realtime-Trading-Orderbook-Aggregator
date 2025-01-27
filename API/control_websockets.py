import asyncio
from .binance_websocket import BinanceWebSocket
from .deribit_websocket import DeribitWebSocket
import streamlit as st

EXCHANGE_WEBSOCKETS = {
    'Binance': BinanceWebSocket,
    'Deribit': DeribitWebSocket,
    # You can add more exchanges here in the future
}


async def run_api():
    # Create WebSocket instances dynamically based on the session array
    exchange_instances = []
    exchanges = st.session_state.get("exchange_choices")

    for exchange_name in exchanges:
        if exchange_name in EXCHANGE_WEBSOCKETS:
            # Instantiate the WebSocket class for the given exchange
            exchange_class = EXCHANGE_WEBSOCKETS[exchange_name]
            exchange_instance = exchange_class(depth=5)  # You can modify the arguments if needed
            exchange_instances.append(exchange_instance)
            print(f"Initialized {exchange_name} WebSocket")  # Debugging line

        else:
            print(f"Error: WebSocket for exchange '{exchange_name}' is not defined.")

    # Run all WebSockets concurrently
    if exchange_instances:
        await asyncio.gather(*(exchange.start() for exchange in exchange_instances))
    else:
        print("No valid WebSockets were initialized.")


async def close_websockets():
    for exchange_name, exchange_class in EXCHANGE_WEBSOCKETS.items():
        exchange_instance = exchange_class()
        if exchange_instance.websocket:
            await exchange_instance.websocket.close()
            print(f"[{exchange_name}] WebSocket connection closed")
