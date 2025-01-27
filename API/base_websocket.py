import asyncio
import websockets
import json
import redis.asyncio as redis
import streamlit as st

class ExchangeWebSocket:
    def __init__(self, exchange_name: str, redis_host: str = 'localhost', redis_port: int = 6379):
        self.exchange_name = exchange_name
        self.uri = None  # To be defined in subclasses
        self.msg = None  # Subscription message format (to be defined in subclasses)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.websocket = None

    async def connect(self):
        """Connects to the WebSocket server and subscribes to data."""
        while True:
            try:
                self.websocket = await websockets.connect(self.uri)
                # print(f"[{self.exchange_name}] Connected to WebSocket")
                await self.subscribe()
                break
            except Exception as e:
                # print(f"[{self.exchange_name}] Error while connecting: {e}")
                await asyncio.sleep(5)  # Retry after 5 seconds

    async def subscribe(self):
        """Subscribes to the WebSocket stream (to be implemented by subclasses)."""
        raise NotImplementedError("Each exchange must implement its own subscription logic")

    async def update_redis(self, bids, asks):
        """Updates Redis with order book data."""
        try:
            redis_key = st.session_state["redis_key"]
            await self.redis.zadd(f"{redis_key}_bids", {bid[0]: float(bid[1]) for bid in bids})
            await self.redis.zadd(f"{redis_key}_asks", {ask[0]: float(ask[1]) for ask in asks})
        except Exception as e:
            print(f"[{self.exchange_name}] Error updating Redis: {e}")

    async def handle_messages(self):
        """Handles incoming WebSocket messages (to be implemented by subclasses)."""
        raise NotImplementedError("Each exchange must implement its own message handling")

    async def start(self):
        """Starts the WebSocket connection and begins retrieving data."""
        await self.connect()
        await self.handle_messages()
