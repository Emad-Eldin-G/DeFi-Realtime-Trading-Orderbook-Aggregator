import asyncio
import json

import streamlit as st
import websockets

from .base_websocket import ExchangeWebSocket


class DeribitWebSocket(ExchangeWebSocket):
    def __init__(
        self, depth: int = 5, redis_host: str = "localhost", redis_port: int = 6379
    ):
        super().__init__("Deribit", redis_host, redis_port)
        self.uri = "wss://test.deribit.com/ws/api/v2"
        base_instrument_name_dict = {
            "BTC": "BTC-PERPETUAL",
            "ETH": "ETH-PERPETUAL",
            "XRP": "XRP-PERPETUAL",
        }
        self.instrument_name = base_instrument_name_dict[st.session_state["currency_1"]]
        self.depth = depth
        self.msg = {
            "jsonrpc": "2.0",
            "id": 8772,
            "method": "public/get_order_book",
            "params": {"instrument_name": self.instrument_name, "depth": self.depth},
        }

    async def subscribe(self):
        """Sends an initial order book request to Deribit."""
        await self.websocket.send(json.dumps(self.msg))

    async def handle_messages(self):
        """Handles incoming Deribit WebSocket messages and correctly updates Redis."""
        while True:
            try:
                response = await self.websocket.recv()
                data = json.loads(response)

                if "params" in data and "data" in data["params"]:
                    order_book = data["params"]["data"]
                    is_snapshot = order_book.get("type") == "snapshot"

                    bids = order_book.get("bids", [])
                    asks = order_book.get("asks", [])

                    await self.update_redis(bids, asks, is_snapshot)

            except websockets.exceptions.ConnectionClosed:
                await self.connect()
                await self.subscribe()
            except Exception as e:
                await asyncio.sleep(5)  # Retry after a delay
