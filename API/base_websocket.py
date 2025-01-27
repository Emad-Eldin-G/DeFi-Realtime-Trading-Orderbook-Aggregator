import asyncio
import os

import redis
import streamlit as st
import websockets


class ExchangeWebSocket:
    def __init__(
        self, exchange_name: str, redis_host: str = "localhost", redis_port: int = 6379
    ):
        self.exchange_name = exchange_name
        self.uri = None  # To be defined in subclasses
        self.msg = None  # Subscription message format (to be defined in subclasses)

        # Run redis based on the environment (docker currently)
        redis_host = os.getenv("REDIS_HOST")  # Use service name in Docker
        redis_port = int(os.getenv("REDIS_PORT"))
        self.redis = redis.Redis(
            host=redis_host, port=redis_port, db=0, decode_responses=True
        )

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
        raise NotImplementedError(
            "Each exchange must implement its own subscription logic"
        )

    async def update_redis(self, bids, asks, is_snapshot):
        """Updates Redis with order book data. If it's a snapshot, clear old data."""
        try:
            redis_key = st.session_state["redis_key"]

            if is_snapshot:
                self.redis.delete(f"{redis_key}_bids")  # Clear old bids
                self.redis.delete(f"{redis_key}_asks")  # Clear old asks

            self.redis.zadd(
                f"{redis_key}_bids", {bid[0]: float(bid[1]) for bid in bids}
            )
            self.redis.zadd(
                f"{redis_key}_asks", {ask[0]: float(ask[1]) for ask in asks}
            )

        except Exception as e:
            print(f"[{self.exchange_name}] Error updating Redis: {e}")

    async def handle_messages(self):
        """Handles incoming WebSocket messages (to be implemented by subclasses)."""
        raise NotImplementedError(
            "Each exchange must implement its own message handling"
        )

    async def start(self):
        """Starts the WebSocket connection and begins retrieving data."""
        await self.connect()
        await self.handle_messages()
