import pandas as pd
import redis.asyncio as redis
import asyncio
import streamlit as st

class OrderBookAggregator:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = None
        self.redis_host = redis_host
        self.redis_port = redis_port

    async def connect(self):
        """Initialize async Redis connection."""
        self.redis = await redis.Redis(host=self.redis_host, port=self.redis_port, db=0, decode_responses=True)

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

        order_book_df = pd.DataFrame({
            "Size (Bids)": [b[1] for b in bids],
            "Bid Price": [b[0] for b in bids],
            "Ask Price": [a[0] for a in asks],
            "Size (Asks)": [a[1] for a in asks]
        })

        return order_book_df

def format_number(value):
    """Formats large numbers with K (thousands) and M (millions)"""
    try:
        value = float(value)  # Ensure numeric type
        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:.5f}"  # Ensure two decimal places
    except (ValueError, TypeError):
        return value  # Return as-is if not a number


@st.fragment
def order_book_display(data):
    st.write("## Order Book")

    max_rows = 20
    data = data.iloc[:max_rows]  # Fix incorrect list slicing on DataFrame

    data["Size (Bids)"] = data["Size (Bids)"].apply(format_number)
    data["Size (Asks)"] = data["Size (Asks)"].apply(format_number)

    # Create DataFrame for structured table
    df = pd.DataFrame({
        "Size": data["Size (Bids)"],
        "Bid": data["Bid Price"],
        "Ask": data["Ask Price"],
        "Size ": data["Size (Asks)"]  # Space added to avoid name clash
    })

    # Display the order book
    st.table(df.style
        .set_properties(subset=["Bid"], **{"color": "green", "font-weight": "bold"})
        .set_properties(subset=["Ask"], **{"color": "red", "font-weight": "bold"})
        .hide(axis="index")
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
