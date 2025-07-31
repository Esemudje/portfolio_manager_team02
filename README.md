# Portfolio Manager

A hackathon project to simulate stock## Getting Started

### Quick Start with Docker (Coming Soon)
```bash
# Clone the repository
git clone https://github.com/your‑team/portfolio‑manager.git
cd portfolio‑manager

# Start everything (backend, frontend, and database)
docker compose up
```

### Manual Setup

#### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   pip install -r ../requirements.txt
   ```

3. Set up environment variables (create `.env` file):
   ```
   ALPHA_VANTAGE_KEY=your_api_key_here
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=portfolio
   ```

4. Start the Flask server:
   ```bash
   python run.py
   ```

#### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open `http://localhost:3000` in your browser

The frontend will automatically proxy API requests to the Flask backend running on port 5000. portfolio tracking.

## What We’re Building

- Simple web app where anyone can sign up, deposit virtual cash, and trade stocks with fake money.
- Real‑time delayed prices fetched from free market data APIs.
- Basic charts and tables to show how a portfolio performs day to day.
- Showing different metrics for the information on portfolio and individual securities deatils. (EXTRA)

## Technology Plan

| Layer       | Tooling                  | Purpose                                                           |
| ----------- | ------------------------ | ----------------------------------------------------------------- |
| Front‑end   | React with Javascript    | Build the user interface and handle page routing                  |
| Back‑end    | Flask (Python)           | Provide REST endpoints for authentication, trading, and analytics |
| Data Store  | MySQL                    | Persist user accounts, trades, and historic profit & loss         |
| Market Data | yFinance or AlphaVantage | Retrieve open, close, and news data for stocks                    |
| Hosting     | Render                   | Deploy a free demo for testing                                    |

## Planned User Stories

### Trading

1. **Buy Stock** – place a buy order with virtual cash.
2. **Sell Stock** – close an existing position.
3. **List Available Stocks** – browse or search tickers before trading.

### Portfolio

4. **Display Current Portfolio** – view holdings, cash balance, and total equity.
5. **See Stock Inventory** – inspect each position with quantity, average cost, and market value.
6. **Trade Logs / History** – timeline of every executed order.
7. **Gainers vs Losers** – quick visual of daily winners and losers.
8. **Performance Indicators** – basic metrics such as total return and daily P\&L.
9. **Individual Stock Indicators** – moving averages, RSI, and other chart overlays (stretch goal).

### Account

10. **Add Profile System** – register, log in, and manage personal details. - **_Only one user for now_**
11. **Add Balance System** – top‑up fake funds; support fake deposits and withdrawals.

### Data & Infrastructure

12. **MySQL Connection** – store users, trades, and historical P\&L tables.
13. **Introduce Caching for API Calls** – reduce the load on free market‑data providers.
14. **News Feed** – surface news headlines relevant to portfolio symbols.
15. **Create Graphs** – render price and portfolio charts for quick insights.
16. **Host on Render** – deploy the full stack to a live URL.

## Using MySQL

MySQL will keep a record of:

- **Users** – authentication details and profile settings. - **_Only one user for now, so just login_**
- **Trades** – every buy or sell order with price, quantity, and timestamp.
- **Holdings** – current share count and cost basis for each symbol.
- **Historic P\&L** – daily snapshots so we can chart performance over time.

## Getting Started

```bash
# Clone the repository
git clone https://github.com/your‑team/portfolio‑manager.git
cd portfolio‑manager

# Start everything (backend, frontend, and database)
docker compose up
```

Open `http://localhost:3000` in your browser and you’re ready to trade.

## Team

Charles, Jay, Yash
