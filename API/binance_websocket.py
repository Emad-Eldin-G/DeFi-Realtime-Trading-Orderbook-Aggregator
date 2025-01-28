import json

import streamlit as st
import websockets

from .base_websocket import ExchangeWebSocket


class BinanceWebSocket(ExchangeWebSocket):
    def __init__(
        self, depth: int = 5, redis_host: str = "localhost", redis_port: int = 6379
    ):
        super().__init__("Binance", redis_host, redis_port)
        self.uri = "wss://stream.binance.com:9443/ws"
        base_intstrument_name_dict = {
            "BTC": "btcusdt",
            "ETH": "ethusdt",
        }
        self.symbol = base_intstrument_name_dict[st.session_state["instrument"]]
        self.depth = depth
        self.msg = {
            "method": "SUBSCRIBE",
            "params": [
                f"{self.symbol}@depth{self.depth}"  # e.g., "btcusdt@depth5" for 5 levels of the order book
            ],
            "id": 1,
        }
        print(f"Binance WebSocket initialized for {self.symbol}")  # Debugging line

    async def subscribe(self):
        """Subscribes to Binance order book."""
        # print(f"Subscribing to Binance WebSocket for {self.symbol}")  # Debugging line
        await self.websocket.send(json.dumps(self.msg))

    async def handle_messages(self):
        """Handles incoming Binance WebSocket messages and correctly updates Redis."""
        received_snapshot = False  # Track if we've received the first snapshot

        while True:
            try:
                response = await self.websocket.recv()
                data = json.loads(response)

                if "bids" in data and "asks" in data:
                    # First message is always a snapshot; track it
                    if not received_snapshot:
                        is_snapshot = True
                        received_snapshot = True
                    else:
                        is_snapshot = False  # Subsequent updates are incremental

                    await self.update_redis(data["bids"], data["asks"], is_snapshot)

            except websockets.exceptions.ConnectionClosed:
                await self.connect()
            except Exception as e:
                pass
