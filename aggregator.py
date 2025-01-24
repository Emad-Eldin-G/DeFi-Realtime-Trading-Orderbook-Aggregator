import redis.asyncio as redis
import asyncio
from db_websocket import run_db_ws
from bi_websocket import run_bi_ws

class OrderBookAggregator:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis = None

    async def connect_redis(self):
        """
        Connect to Redis asynchronously using redis.asyncio.
        """
        self.redis = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        print("Connected to Redis")

    async def get_order_books(self):
        """
        Query Redis for the latest bids and asks from both Binance and Deribit.
        Combine and return the order book data.
        """
        # Fetch the order book data from Redis for Binance and Deribit
        binance_bids = await self.redis.zrange('BTC-PERPETUAL_bids', 0, -1, withscores=True)
        binance_asks = await self.redis.zrange('BTC-PERPETUAL_asks', 0, -1, withscores=True)

        deribit_bids = await self.redis.zrange('BTC-PERPETUAL_bids', 0, -1, withscores=True)
        deribit_asks = await self.redis.zrange('BTC-PERPETUAL_asks', 0, -1, withscores=True)

        # Combine the bids and asks from both exchanges
        combined_bids = sorted(binance_bids + deribit_bids, key=lambda x: x[1], reverse=True)  # Sort by price (score)
        combined_asks = sorted(binance_asks + deribit_asks, key=lambda x: x[1])  # Sort by price (score)

        # Get the best bid and best ask
        best_bid = combined_bids[0] if combined_bids else None
        best_ask = combined_asks[0] if combined_asks else None

        best_bid_price = float(best_bid[0].decode())  # Decode the byte string and convert to float
        best_bid_amount = best_bid[1]  # This value is already a float

        best_ask_price = float(best_ask[0].decode())  # Decode the byte string and convert to float
        best_ask_amount = best_ask[1]  # This value is already a float

        # Return the combined order book
        return {
            'best_bid': best_bid,
            'best_ask': best_ask,
            'combined_bids': combined_bids[:5],  # Top 5 bids
            'combined_asks': combined_asks[:5]   # Top 5 asks
        }

    async def display_order_book(self):
        """
        Continuously display the updated order book.
        """
        while True:
            order_book = await self.get_order_books()
            print("Best Bid:", order_book['best_bid'])
            print("Best Ask:", order_book['best_ask'])
            print("Top 5 Bids:", order_book['combined_bids'])
            print("Top 5 Asks:", order_book['combined_asks'])
            print("------\n")
            await asyncio.sleep(1)  # Sleep for 1 second to simulate continuous display

    async def start(self):
        """
        Start the Redis connection and continuously display the order book.
        """
        await self.connect_redis()
        await self.display_order_book()


# Usage example:
if __name__ == '__main__':
    aggregator = OrderBookAggregator(redis_host='localhost', redis_port=6379)

    loop = asyncio.get_event_loop()
    loop.create_task(aggregator.start())
    loop.create_task(run_bi_ws())
    loop.create_task(run_db_ws())
    loop.run_forever()