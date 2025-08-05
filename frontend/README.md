# Portfolio Manager Frontend

A React-based frontend for the Portfolio Manager application that allows users to trade stocks with virtual money.

## Features

- **Dashboard**: Overview of portfolio performance, holdings, and watchlist
- **Portfolio**: Detailed view of current holdings with charts and trade history
- **Trading**: Search and trade stocks with real-time quotes
- **Stock Details**: In-depth analysis of individual stocks with charts, news, and financial data

## Technology Stack

- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Recharts** - Charts and data visualization
- **Axios** - HTTP client for API calls
- **Lucide React** - Modern icon library

## Getting Started

### Prerequisites

- Node.js 16 or higher
- npm or yarn
- Backend Flask server running on port 5000

### Installation

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

4. Open your browser to `http://localhost:3000`

The app will automatically proxy API requests to `http://localhost:5000` where your Flask backend should be running.

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (not recommended)

## Project Structure

```
src/
├── components/          # React components
│   ├── Dashboard.js     # Main dashboard view
│   ├── Portfolio.js     # Portfolio overview with charts
│   ├── Trading.js       # Stock search and trading interface
│   └── StockDetail.js   # Individual stock analysis
├── services/
│   └── apiService.js    # API communication layer
├── App.js              # Main app component with routing
├── App.css             # Component-specific styles
├── index.js            # React entry point
└── index.css           # Global styles
```

## API Integration

The frontend communicates with your Flask backend through the following endpoints:

- `GET /api/stocks/<symbol>` - Real-time stock quote
- `GET /api/stocks/<symbol>/overview` - Company overview
- `GET /api/stocks/<symbol>/intraday` - Intraday price data
- `GET /api/stocks/<symbol>/daily` - Daily price data
- `GET /api/stocks/<symbol>/news` - News and sentiment
- `GET /api/stocks/<symbol>/earnings` - Earnings data
- `GET /api/test-connection` - Test API connectivity

## Features Overview

### Dashboard
- Portfolio value summary
- Current holdings table
- Watchlist with real-time quotes
- Quick navigation to trading

### Portfolio
- Interactive pie chart of portfolio allocation
- Performance bar chart
- Detailed holdings table with P&L
- Complete trade history

### Trading
- Stock search functionality
- Popular stocks quick access
- Real-time quote display
- Buy/sell order placement
- Order summary and confirmation

### Stock Detail
- Real-time price and change information
- 30-day price chart
- Company overview and financial metrics
- Latest news with sentiment analysis
- Quick buy/sell actions

## Styling

The app uses a modern, responsive design with:
- CSS Grid and Flexbox for layouts
- Gradient backgrounds and subtle shadows
- Hover effects and smooth transitions
- Mobile-responsive design
- Color-coded positive/negative values

## Next Steps

To complete the integration with your backend:

1. **Add Database Integration**: Implement portfolio, holdings, and trade management endpoints in your Flask backend
2. **User Authentication**: Add login/logout functionality
3. **Real Trading Logic**: Connect trade execution to your MySQL database
4. **WebSocket Integration**: Add real-time price updates
5. **Advanced Features**: Add more chart types, alerts, and portfolio analytics

## Development Notes

- The app currently uses mock data for portfolio and holdings
- Real-time stock data comes from your yFinance integration
- Error handling includes network timeouts and API rate limits
- All currency values are formatted consistently
- The design is mobile-responsive

## Troubleshooting

**API Connection Issues:**
- Ensure your Flask backend is running on port 5000
- Check the database connection is configured
- Verify CORS settings if needed

**Build Issues:**
- Clear node_modules and reinstall dependencies
- Check Node.js version compatibility
- Review console for specific error messages
