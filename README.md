# DeFi-Realtime-Orderbook-Aggregator
Realtime aggregator of DeFi instrument order-books from different exchanges

## Local Running Instructions (**Docker**)
1. Clone the repository
2. Make sure you have Docker installed on your machine (https://docs.docker.com/get-docker/)
3. Run `docker-compose up --build` in the root directory (where `docker-compose.yml` is located)
4. The application should be running on `http://0.0.0.0:8501/`
5. To stop the application, run `docker-compose down`
> Note that the app only runs on docker,
> minor changes need to be made with the Redis config if to be run on localhost

### Current supported and implemented exchanges
- Binance
- Deribit
- Coinbase (in progress)


## Notes on the implementation
- Streamlit was used as a frontend UI as it interacts directly with the backend python code, hence no need for additional API or communication complexity.
- Redis was used as the data storage for real-time incoming orderbook updates. Because redis is an in-memory database, it is very fast and can handle the high-frequency updates from the exchanges.
- Docker was used to containerize the application for easy deployment and running on different machines, and docker makes it easier to scale in the future using Kubernetes or other container orchestration tools.

## Areas of improvement
- Use (https://github.com/bmoscon/cryptofeed) for a more uniform interaction with order-books from different exchanged (Instead of reinventing the wheel with different websocket implementations).
- Use InfluxDB to keep a capture of the order-book data for use in backtesting and other analytics (Keep redis for the real-time data interaction).
- Construct a more robust error handling framework so that the application can recover from errors and continue running.
- Fetch more details alongside the orderbook data to provide a more comprehensive view of the market.
