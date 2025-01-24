import asyncio
import websockets
import json
import redis.asyncio as redis

class DeribitWebSocket:
    def __init__(self, uri: str, instrument_name: str = "BTC-PERPETUAL", depth: int = 5, redis_host: str = 'localhost', redis_port: int = 6379):
        self.uri = uri
        self.instrument_name = instrument_name
        self.depth = depth
        self.websocket = None
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.msg = {
            "jsonrpc": "2.0",
            "id": 8772,
            "method": "public/get_order_book",
            "params": {
                "instrument_name": self.instrument_name,
                "depth": self.depth
            }
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
                await self.send_order_book_request()
                break  # Exit the loop once connected and subscribed
            except Exception as e:
                print(f"Error while connecting: {e}")
                await asyncio.sleep(5)  # Wait 5 seconds before trying again

    async def send_order_book_request(self):
        """
        Sends a request to get the order book for the instrument.
        """
        await self.websocket.send(json.dumps(self.msg))

    async def update_redis(self, data):
        """
        Updates the Redis database with the new order book data (bids/asks).
        """
        try:
            # Extract bids and asks and store them in Redis
            bids = {str(bid[0]): float(bid[1]) for bid in data['result']['bids']}
            asks = {str(ask[0]): float(ask[1]) for ask in data['result']['asks']}

            # Store bids and asks in Redis sorted sets (price => quantity)
            await self.redis.zadd(f"{self.instrument_name}_bids", bids)
            await self.redis.zadd(f"{self.instrument_name}_asks", asks)

            print(f"Updated Redis with {self.instrument_name} order book data")

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
                if 'result' in data and 'bids' in data['result'] and 'asks' in data['result']:
                    print("Updated Order Book:", data)

                    # Update Redis with the new order book data
                    await self.update_redis(data)

                # Send the same message again to keep the request alive
                await self.websocket.send(json.dumps(self.msg))

            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed. Reconnecting...")
                await self.connect()
                await self.send_order_book_request()
            except Exception as e:
                print(f"Error while receiving data: {e}")
                await asyncio.sleep(5)  # Wait 5 seconds before attempting to reconnect in case of other errors

    async def start(self):
        """
        Starts the WebSocket connection and begins retrieving the order book.
        """
        await self.connect()
        await self.get_order_book()

# Usage example:
async def run_db_ws():
    # Instantiate the WebSocket client
    ws_client = DeribitWebSocket(
        uri='wss://test.deribit.com/ws/api/v2',
        instrument_name="BTC-PERPETUAL",
        depth=5,
        redis_host='localhost',
        redis_port=6379)

    # Start the WebSocket connection and get the order book
    await ws_client.start()