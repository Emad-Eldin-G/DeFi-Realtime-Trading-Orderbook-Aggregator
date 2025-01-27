import os

import pandas as pd
import redis.asyncio as redis
import streamlit as st


class OrderBookAggregator:
    def __init__(self):
        pd.options.display.float_format = "{:.2f}".format
        self.redis = None
        self.redis_host = os.getenv("REDIS_HOST")  # Use service name in Docker
        self.redis_port = int(os.getenv("REDIS_PORT"))

    async def connect(self):
        """Initialize async Redis connection."""
        self.redis = await redis.Redis(
            host=self.redis_host, port=self.redis_port, decode_responses=True
        )

    async def get_order_books(self):
        """
        Fetch and format order book data from Redis.
        """
        redis_key = st.session_state.get("redis_key", "default_key")

        # Fetch bids and asks from Redis
        bids = await self.redis.zrevrange(f"{redis_key}_bids", 0, 19, withscores=True)
        asks = await self.redis.zrange(f"{redis_key}_asks", 0, 19, withscores=True)

        # Convert bytes to float for readability
        def process_orders(order_list):
            return [(float(price), amount) for price, amount in order_list]

        bids = process_orders(bids)
        asks = process_orders(asks)

        # Convert to DataFrame for better table formatting
        max_len = max(len(bids), len(asks))
        bids += [("", "")] * (max_len - len(bids))  # Pad shorter list
        asks += [("", "")] * (max_len - len(asks))  # Pad shorter list

        order_book_df = pd.DataFrame(
            {
                "Size (Bids)": [b[1] for b in bids],
                "Bid Price": [b[0] for b in bids],
                "Ask Price": [a[0] for a in asks],
                "Size (Asks)": [a[1] for a in asks],
            }
        )

        return order_book_df


def format_number(x):
    try:
        x = float(x)  # Convert string to float
        if x >= 1_000_000:
            return f"{x / 1_000_000:.2f}M"
        elif x >= 1_000:
            return f"{x / 1_000:.2f}K"
        return f"{x:.5f}"
    except ValueError:
        return str(x)  # If conversion fails, return as is


@st.fragment
def order_book_display(data):
    st.write("## Order Book")

    max_rows = 20
    data = data.iloc[:max_rows]  # Fix incorrect list slicing on DataFrame

    data["Size (Bids)"] = data["Size (Bids)"].apply(format_number)
    data["Size (Asks)"] = data["Size (Asks)"].apply(format_number)

    # Create DataFrame for structured table
    df = pd.DataFrame(
        {
            "Size": data["Size (Bids)"],
            "Bid": data["Bid Price"],
            "Ask": data["Ask Price"],
            "Size ": data["Size (Asks)"],
        }
    )

    df.assign(hack="").set_index("hack")

    # Display the order book
    st.table(
        df.style.set_properties(
            subset=["Bid"], **{"color": "green", "font-weight": "bold"}
        ).set_properties(subset=["Ask"], **{"color": "red", "font-weight": "bold"})
    )


async def run_aggregator():
    aggregator = OrderBookAggregator()
    await aggregator.connect()  # Ensure Redis connection is established
    container = st.empty()
    while True:
        order_books = await aggregator.get_order_books()
        with container:
            order_book_display(order_books)
        print(order_books)  # Debugging output (can be removed)
