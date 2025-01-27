import pytest
import pandas as pd
import redis.asyncio as redis
from unittest.mock import AsyncMock, patch
from aggregator import OrderBookAggregator, format_number

@pytest.mark.asyncio
async def test_get_order_books():
    """Test order book aggregation using a mock Redis instance."""

    mock_redis = AsyncMock()
    mock_redis.zrevrange.return_value = [(b"100", 1.5), (b"99.5", 2.0)]
    mock_redis.zrange.return_value = [(b"101", 1.0), (b"101.5", 1.2)]

    with patch.object(redis, "Redis", return_value=mock_redis):
        aggregator = OrderBookAggregator()
        order_book_df = await aggregator.get_order_books()

    assert isinstance(order_book_df, pd.DataFrame)
    assert len(order_book_df) == 2  # Ensure two rows exist

    # ✅ Check bid prices
    assert order_book_df.iloc[0]["Bid Price"] == 100.0
    assert order_book_df.iloc[1]["Bid Price"] == 99.5

    # ✅ Check ask prices
    assert order_book_df.iloc[0]["Ask Price"] == 101.0
    assert order_book_df.iloc[1]["Ask Price"] == 101.5


def test_format_number():
    """Test number formatting logic."""
    assert format_number(1500) == "1.50K"
    assert format_number(2500000) == "2.50M"
    assert format_number(42) == "42.00"
    assert format_number("invalid") == "invalid"  # Should return as-is for non-numbers
