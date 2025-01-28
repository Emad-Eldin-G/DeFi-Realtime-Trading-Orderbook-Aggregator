import asyncio

import streamlit as st

from API.control_websockets import run_api
from aggregator import run_aggregator


def configure_page():
    st.set_page_config(
        page_title="DeFi Orderbook Aggregator",
        page_icon="🌐💰",
        layout="wide",
        initial_sidebar_state="auto",
    )

    # CSS styling
    st.markdown(
        """
        <style>
        </style>
        """,
        unsafe_allow_html=True,
    )


def configure_sidebar():
    st.sidebar.markdown(
        "## Created by [EmadEldin Osman](https://github.com/Emad-Eldin-G)"
    )
    st.sidebar.divider()
    st.sidebar.markdown("""
    ### Powered by:  
    - [Redis](https://streamlit.io/)
    - [InfluxDB](https://pandas.pydata.org/)
    - [Streamlit](https://numpy.org/)  
    - [Websockets](https://pandas-ai.com/)
    
    ### Currently Supports:
    - [Binance](https://binance.com/)
    - [Deribit](https://deribit.com/)
    - BTC instrument
    - ETH instrument
    > Note that instrument naming differs based on exchanges (use usd for currency 2 and Deribit will use perpetual in the backend)
    """)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)


def header():
    st.markdown(
        """
        <div style="background-color:#464e5f;padding:10px;border-radius:10px">
        <h1 style="color:white;text-align:center;">DeFi Orderbook Aggregator</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("#")


def exchange_choice_form():
    st.subheader("Choose the exchange you want to track")
    st.multiselect(
        "Exchange",
        ["Binance", "Deribit"],
        default=["Binance", "Deribit"],
        key="exchange_choices",
    )
    st.write("#")


def instrument_choice_multiselect():
    st.subheader("Enter the instrument you want to track", "BTC")
    st.selectbox(
        "Instrument",
        ["BTC", "ETH"],
        key="instrument",
    )

    st.session_state["redis_key"] = st.session_state["instrument"]


def main():
    configure_page()
    configure_sidebar()
    header()
    exchange_choice_form()
    instrument_choice_multiselect()
    if st.button("Start", key="start_button"):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.create_task(run_api())
            loop.create_task(run_aggregator())
            loop.run_forever()
        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
