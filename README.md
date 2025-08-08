# Portfolio Manager

A comprehensive portfolio management application built for tracking investments, trading stocks, and analyzing performance.

## Features

### 🔍 **Enhanced Stock Search**

- **Search by Company Name**: Find stocks using full company names (e.g., "Apple", "Microsoft")
- **Smart Autocomplete**: Real-time search suggestions with company details
- **Sector-Based Display**: Visual indicators with emojis for different sectors (💻 Technology, 🏥 Healthcare, etc.)
- **Market Cap Information**: See market capitalization for informed decisions
- **Priority Search**: Exact symbol matches get priority in search results

### 📊 **Portfolio Management**

- Real-time portfolio tracking with live price updates
- Comprehensive P&L calculations (realized and unrealized)
- Holdings management with average cost basis
- Cash balance management with deposit/withdrawal capabilities

### 💹 **Enhanced Trading Interface**

- **Multiple Order Types**: Support for Market, Limit, Stop, and Stop-Limit orders
- **Market Orders**: Buy/sell immediately at current market price for speed
- **Limit Orders**: Buy/sell only at specified price or better for price control
- **Stop Orders**: Trigger market order when stop price is reached for loss protection
- **Stop-Limit Orders**: Trigger limit order when stop price is reached for precise control
- **Pending Order Management**: View and cancel pending orders
- **Real-time Order Execution**: Background service monitors and executes orders
- **Order Validation**: Comprehensive validation and error handling
- **Enhanced UI**: Modern interface with order type selection and visual indicators

### 📋 **Watchlist**

- Enhanced watchlist with smart stock search
- Add stocks by searching company names instead of just symbols
- Real-time price updates for watched stocks
- Easy removal of stocks from watchlist

### 📰 **Market News**

- Latest market news and updates
- Sentiment analysis on news articles
- Related stock recommendations

## Technology Stack

| Component   | Technology            | Purpose                                                           |
| ----------- | --------------------- | ----------------------------------------------------------------- |
| Front‑end   | React with Javascript | Build the user interface and handle page routing                  |
| Back‑end    | Flask (Python)        | Provide REST endpoints for authentication, trading, and analytics |
| Data Store  | MySQL                 | Persist user accounts, trades, and historic profit & loss         |
| Market Data | yFinance              | Retrieve open, close, and news data for stocks                    |
| Search Data | NASDAQ Companies DB   | Enhanced search with 6000+ companies, sectors, and market caps    |

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
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=portfolio_manager
   ```

4. Set up the database:

   ```bash
   # Create database and tables
   mysql -u root -p < ../sql/default_portfolio.sql

   # Import NASDAQ companies data for enhanced search
   mysql -u root -p < ../sql/Nasdaq\ Full\ Sector\ Marketcap.sql

   ```

5. Start the Flask server:
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
git clone <repository-url>
cd portfolio_manager_team02

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r ../requirements.txt

# Set up frontend
cd ../frontend
npm install

# Start servers
# Terminal 1 (Backend)
cd backend && python run.py

# Terminal 2 (Frontend)
cd frontend && npm start
```

## API Endpoints

### Enhanced Search Endpoints

```
GET /api/search/stocks?q={query}&limit={limit}
```

Search for stocks by company name or symbol. Returns results sorted by market cap with sector information.

**Example Response:**

```json
{
  "query": "apple",
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc. Common Stock",
      "sector": "Technology",
      "market_cap": 3233720981000,
      "market_cap_formatted": "$3.2T",
      "sector_emoji": "💻",
      "display_name": "💻 Apple Inc. Common Stock"
    }
  ],
  "count": 1
}
```

```
GET /api/search/stocks/{symbol}/details
```

Get detailed information for a specific stock symbol.

```
GET /api/search/sectors
```

Get all available sectors for filtering.

```
GET /api/search/top-stocks?sector={sector}&limit={limit}
```

Get top stocks by market cap, optionally filtered by sector.

### Enhanced Trading Endpoints with Order Types

```
POST /api/orders
```

Place an order with specified order type. Supports Market, Limit, Stop, and Stop-Limit orders.

**Request Body:**

```json
{
  "symbol": "AAPL",
  "side": "BUY",
  "quantity": 10,
  "order_type": "LIMIT",
  "price": 150.0,
  "stop_price": null,
  "limit_price": null,
  "user_id": "default_user"
}
```

**Order Types:**

- `MARKET`: Execute immediately at current market price
- `LIMIT`: Execute only at specified price or better (requires `price`)
- `STOP`: Trigger market order when `stop_price` is reached
- `STOP_LIMIT`: Trigger limit order at `limit_price` when `stop_price` is reached

```
GET /api/orders?user_id={userId}&symbol={symbol}
```

Get pending orders for a user, optionally filtered by symbol.

```
DELETE /api/orders/{orderId}?user_id={userId}
```

Cancel a pending order.

```
POST /api/orders/check-execution
```

Manually trigger order execution check (for testing).

### Legacy Trading Endpoints

```
GET /api/stocks/{symbol}           # Get stock quote
POST /api/trading/buy              # Buy stock (market order)
POST /api/trading/sell             # Sell stock (market order)
GET /api/portfolio                 # Get portfolio summary
GET /api/portfolio/balance         # Get cash balance
GET /api/news                      # Get market news
```

## Usage Examples

### Enhanced Search in Trading

1. Navigate to the Trading page
2. Start typing a company name (e.g., "Microsoft", "Apple", "Tesla")
3. Select from the dropdown with company details, sector icons, and market cap
4. Continue with your trade

### Enhanced Watchlist

1. Go to the Dashboard
2. In the Watchlist section, use the search box to find companies
3. Add stocks by name instead of memorizing symbols
4. View real-time prices with sector indicators

## Database Schema

The application now includes an enhanced database schema with NASDAQ companies data and order management:

### Core Tables

- `holdings`: Current portfolio positions with average cost basis
- `trades`: Historical trade records with P&L calculations
- `user_balance`: Cash balance management
- `nasdaq_companies`: 6000+ companies with symbols, names, sectors, and market caps

### Enhanced Order Management Tables

- `orders`: Pending orders with support for different order types
  - Order types: MARKET, LIMIT, STOP, STOP_LIMIT
  - Order status: PENDING, FILLED, CANCELLED, EXPIRED
  - Time in force: DAY, GTC (Good Till Cancelled)
  - Price fields for limit and stop prices

### Order Type Examples

**Market Order**

```sql
INSERT INTO orders (stock_symbol, order_type, side, quantity, status)
VALUES ('AAPL', 'MARKET', 'BUY', 10, 'PENDING');
```

**Limit Order**

```sql
INSERT INTO orders (stock_symbol, order_type, side, quantity, price, status)
VALUES ('AAPL', 'LIMIT', 'BUY', 10, 150.00, 'PENDING');
```

**Stop Order**

```sql
INSERT INTO orders (stock_symbol, order_type, side, quantity, stop_price, status)
VALUES ('AAPL', 'STOP', 'SELL', 10, 140.00, 'PENDING');
```

**Stop-Limit Order**

```sql
INSERT INTO orders (stock_symbol, order_type, side, quantity, stop_price, limit_price, status)
VALUES ('AAPL', 'STOP_LIMIT', 'SELL', 10, 140.00, 138.00, 'PENDING');
```

### Search Features

- **Fuzzy Name Search**: Find companies by partial name matches
- **Symbol Priority**: Exact symbol matches get highest priority
- **Sector Filtering**: Visual sector indicators with emojis
- **Market Cap Sorting**: Results sorted by market capitalization
- **Smart Autocomplete**: Real-time suggestions as you type

## Sector Emojis

- 💻 Technology
- 🏥 Health Care
- 💰 Finance
- 🛍️ Consumer Discretionary
- 🛒 Consumer Staples
- 🏭 Industrials
- ⚗️ Basic Materials
- ⚡ Energy
- 🏠 Real Estate
- ⚙️ Utilities
- 📡 Communication Services
  git clone https://github.com/your‑team/portfolio‑manager.git
  cd portfolio‑manager

# Start everything (backend, frontend, and database)

docker compose up

```

Open `http://localhost:3000` in your browser and you’re ready to trade.

## Team

Charles, Jay, Yash
```
