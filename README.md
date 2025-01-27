# DeFi-Realtime-Orderbook-Aggregator
Realtime aggregator of DeFi instrument order-books from different exchanges

## Local Running Instructions (**Docker**)
1. Clone the repository
2. Make sure you have Docker installed on your machine (https://docs.docker.com/get-docker/)
3. Run `docker-compose up --build` in the root directory (where `docker-compose.yml` is located)
4. The application should be running on `http://0.0.0.0:8501/`
5. To stop the application, run `docker-compose down`

### Current supported and implemented exchanges
- Binance
- Deribit
- Coinbase (in progress)
