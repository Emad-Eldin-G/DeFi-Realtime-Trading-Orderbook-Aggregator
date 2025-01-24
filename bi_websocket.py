import asyncio
import websockets
import json
import redis.asyncio as redis

class BinanceWebSocket:
    def __init__(self, uri: str, symbol: str = "btcusdt", depth: int = 5, redis_host: str = 'localhost', redis_port: int = 6379):
        self.uri = uri
        self.symbol = symbol
        self.depth = depth
        self.websocket = None
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.msg = {
            "method": "SUBSCRIBE",
            "params": [
                f"{self.symbol}@depth{self.depth}"  # e.g., "btcusdt@depth5" for 5 levels of the order book
            ],
            "id": 1
        }

    async def connect(self):
        """
        Connects to the WebSocket server.
        """
        while True:  # Infinite loop to reconnect after the connection closes
            try:
                # Connect to the WebSocket
                self.websocket = await websockets.connect(self.uri)
                print("Connected to WebSocket")
                await self.send_subscription_request()
                break  # Exit the loop once connected and subscribed
            except Exception as e:
                print(f"Error while connecting: {e}")

    async def send_subscription_request(self):
        """
        Sends a subscription request to get the order book for the symbol.
        """
        await self.websocket.send(json.dumps(self.msg))

    async def update_redis(self, data):
        """
        Updates the Redis database with the new order book data (bids/asks).
        """
        try:
            # Store the bids and asks in Redis
            await self.redis.zadd(f"{self.symbol}_bids", {bid[0]: float(bid[1]) for bid in data['bids']})
            await self.redis.zadd(f"{self.symbol}_asks", {ask[0]: float(ask[1]) for ask in data['asks']})

            print(f"Updated Redis with {self.symbol} order book data")

        except Exception as e:
            print(f"Error while updating Redis: {e}")

    async def get_order_book(self):
        """
        Listens for the updated order book and handles incoming messages.
        """
        while True:
            try:
                response = await self.websocket.recv()
                data = json.loads(response)

                # Only process the order book update if there's data in bids/asks
                if "bids" in data and "asks" in data:
                    print("Updated Order Book:", data)

                    # Update Redis with the new order book data
                    await self.update_redis(data)

            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed. Reconnecting...")
                await self.connect()
            except Exception as e:
                print(f"Error while receiving data: {e}")

    async def start(self):
        """
        Starts the WebSocket connection and begins retrieving the order book.
        """
        await self.connect()
        await self.get_order_book()


# Usage example:
async def run_bi_ws():
    # Instantiate the WebSocket client for Binance
    ws_client = BinanceWebSocket(
        uri='wss://stream.binance.com:9443/ws',
        symbol="btcusdt",
        depth=5,
        redis_host='localhost',
        redis_port=6379
    )

    # Start the WebSocket connection and get the order book
    await ws_client.start()