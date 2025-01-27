import json
import asyncio
import websockets
import streamlit as st
from .base_websocket import ExchangeWebSocket


class DeribitWebSocket(ExchangeWebSocket):
    def __init__(self, depth: int = 5, redis_host: str = 'localhost', redis_port: int = 6379):
        super().__init__("Deribit", redis_host, redis_port)
        self.uri = "wss://test.deribit.com/ws/api/v2"
        base_instrument_name_dict = {"BTC": "BTC-PERPETUAL", "ETH": "ETH-PERPETUAL", "XRP": "XRP-PERPETUAL"}
        self.instrument_name = base_instrument_name_dict[st.session_state["currency_1"]]
        self.depth = depth
        self.msg = {
            "jsonrpc": "2.0",
            "id": 8772,
            "method": "public/get_order_book",
            "params": {"instrument_name": self.instrument_name, "depth": self.depth}
        }

    async def subscribe(self):
        """Sends an initial order book request to Deribit."""
        await self.websocket.send(json.dumps(self.msg))

    async def handle_messages(self):
        """Handles incoming Deribit WebSocket messages."""
        while True:
            try:
                response = await self.websocket.recv()
                data = json.loads(response)
                if "result" in data and "bids" in data["result"] and "asks" in data["result"]:
                    bids = data["result"]["bids"]
                    asks = data["result"]["asks"]
                    await self.update_redis(bids, asks)

                # Send another request to keep fetching the order book
                await self.websocket.send(json.dumps(self.msg))

            except websockets.exceptions.ConnectionClosed:
                # print("[Deribit] WebSocket disconnected. Reconnecting...")
                await self.connect()
                await self.subscribe()
            except Exception as e:
                # print(f"[Deribit] Error receiving data: {e}")
                await asyncio.sleep(5)  # Retry after a short delay
