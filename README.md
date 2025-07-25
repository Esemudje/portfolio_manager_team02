# Portfolio Manager - Team 02 🚀

A hackathon-style portfolio management system built with Flask backend, Next.js frontend, and Python analytics. This project enables users to manage investment portfolios, execute trades, and analyze performance with real-time data visualization.

## 🎯 Project Overview

This portfolio management application allows users to:

- Track and manage investment portfolios with $1,000 starting seed money
- Execute buy/sell orders for stocks and securities
- View real-time portfolio performance and analytics
- Analyze portfolio trends with Python-powered data science
- Generate insights and performance reports

**Starting Seed Money**: Users begin with $1,000 in virtual currency for trading simulation.

## 🏗️ Simple Architecture

Hackathon-focused architecture emphasizing rapid development and core functionality:

### Frontend (Next.js)

- **Technology**: Next.js 14+ with JavaScript (keeping it simple)
- **Styling**: Tailwind CSS for rapid UI development
- **State Management**: React built-in state (useState, useContext)
- **API Communication**: Fetch API for REST calls
- **Charts**: Chart.js for portfolio visualizations

### Backend (Flask)

- **Technology**: Python 3.9+ with Flask
- **Framework**: Flask (Flask-SQLAlchemy, Flask-CORS)
- **Database**: MySQL for data persistence
- **Authentication**: Single user
- **API**: RESTful endpoints returning JSON

### Analytics Engine (Python)

- **Technology**: Integrated within Flask backend
- **Libraries**: Pandas, NumPy, Matplotlib, Plotly
- **Purpose**: Portfolio analysis, risk assessment, trend calculation
- **Integration**: Direct function calls within Flask routes

### Communication

- **Frontend ↔ Backend**: REST API calls (JSON)
- **Analytics**: Integrated Python functions within Flask backend
- **Database**: MySQL with SQLAlchemy ORM

## 📅 3-Day Sprint Plan

### Day 1: Foundation & Backend Core

**Sprint Goal**: Establish project structure and core backend functionality

#### Morning (4 hours)

- [x] Project setup and repository structure
- [ ] Flask project initialization with virtual environment
- [ ] MySQL database setup and connection
- [ ] Basic data models (User, Portfolio, Stock, Transaction)
- [ ] Database schema creation with SQLAlchemy

#### Afternoon (4 hours)

- [ ] Core Flask routes for user management
- [ ] Portfolio CRUD operations
- [ ] Basic authentication (session-based)
- [ ] Stock data integration (mock or free API)
- [ ] Basic error handling and validation

### Day 2: Frontend Development & API Integration

**Sprint Goal**: Build responsive frontend and integrate with backend APIs

#### Morning (4 hours)

- [ ] Next.js project setup (JavaScript, no TypeScript for speed)
- [ ] Login/Register pages with simple forms
- [ ] Dashboard layout with navigation
- [ ] Portfolio overview component
- [ ] API service functions using fetch

#### Afternoon (4 hours)

- [ ] Trading interface (buy/sell forms)
- [ ] Transaction history display
- [ ] Basic portfolio charts with Chart.js
- [ ] Responsive design with Tailwind CSS
- [ ] Frontend-backend integration and testing

### Day 3: Python Analytics & Polish

**Sprint Goal**: Add analytics capabilities and finalize the application

#### Morning (4 hours)

- [ ] Portfolio analytics functions within Flask
- [ ] Risk assessment calculations (Sharpe ratio, volatility)
- [ ] Performance metrics (returns, profit/loss)
- [ ] Data visualization endpoints (charts data)
- [ ] Portfolio optimization suggestions

#### Afternoon (4 hours)

- [ ] Analytics dashboard in frontend
- [ ] Advanced charts and visualizations
- [ ] Portfolio insights and recommendations
- [ ] Final testing and bug fixes
- [ ] Demo preparation and documentation

## 🛠️ Technology Stack

### Backend (Flask)

```
- Python 3.9+
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- MySQL
- Pandas
- NumPy
- Matplotlib/Plotly
- Requests (for market data)
```

### Frontend (Next.js)

```
- Next.js 14+
- JavaScript (ES6+)
- React 18+
- Tailwind CSS
- Chart.js
- Fetch API
```

### Analytics (Integrated Python)

```
- Pandas for data manipulation
- NumPy for calculations
- Matplotlib/Plotly for visualizations
- Scikit-learn for portfolio optimization
- yfinance for stock data (optional)
```

## 📁 Project Structure

```
portfolio_manager_team02/
├── README.md
├── backend/                 # Flask Backend
│   ├── app.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   ├── stock.py
│   │   └── transaction.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── portfolio.py
│   │   ├── trading.py
│   │   └── analytics.py
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── performance.py
│   │   ├── risk_analysis.py
│   │   └── visualizations.py
│   ├── config.py
│   ├── requirements.txt
│   └── database_init.py
├── frontend/               # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.js
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   └── layout.js
│   │   ├── components/
│   │   │   ├── Portfolio/
│   │   │   ├── Trading/
│   │   │   ├── Analytics/
│   │   │   └── UI/
│   │   ├── lib/
│   │   │   ├── api.js
│   │   │   └── utils.js
│   │   └── styles/
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
└── docs/
    ├── setup_guide.md
    └── api_documentation.md
```

## 🔧 Core Features

### User Management

- User registration and authentication
- Profile management
- Portfolio initialization with $1,000 seed money

### Portfolio Management

- Create and manage multiple portfolios
- Real-time portfolio valuation
- Asset allocation tracking
- Performance metrics

### Trading System

- Buy/sell stock orders
- Order history and tracking
- Market data integration
- Transaction fees calculation

### Analytics & Reporting

- Portfolio performance analysis
- Risk assessment metrics
- Trend analysis and predictions
- Custom reports generation

## 🚀 API Endpoints

### Portfolio Management

```
GET    /api/portfolios
POST   /api/portfolios
GET    /api/portfolios/{id}
PUT    /api/portfolios/{id}
DELETE /api/portfolios/{id}
```

### Trading

```
POST /api/trades/buy
POST /api/trades/sell
GET  /api/trades/history
GET  /api/market/stocks
GET  /api/market/stocks/{symbol}
```

### Analytics (Python Service)

```
GET  /analytics/portfolio/{id}/performance
GET  /analytics/portfolio/{id}/risk
POST /analytics/portfolio/optimize
GET  /analytics/market/trends
```

## � Core Hackathon Features

### MVP (Minimum Viable Product)

- **User Authentication**: Simple login/register system
- **Portfolio Dashboard**: Overview of holdings and performance
- **Trading System**: Buy/sell stocks with $1,000 seed money
- **Analytics**: Basic portfolio metrics and visualizations
- **Transaction History**: Record and display all trades

### Enhanced Features (If Time Permits)

- **Advanced Analytics**: Sharpe ratio, volatility calculations
- **Portfolio Optimization**: Python-powered suggestions
- **Market Data Integration**: Real stock prices
- **Interactive Charts**: Detailed portfolio performance graphs
- **Risk Assessment**: Portfolio risk analysis

## 🔐 Simple Security

- Session-based authentication (no JWT complexity)
- Basic input validation
- SQL injection prevention via SQLAlchemy
- CORS setup for frontend-backend communication

## 📊 Database Schema (MySQL)

### Core Tables

```sql
Users: id, username, email, password_hash, cash_balance, created_at
Portfolios: id, user_id, name, total_value, created_at
Stocks: id, symbol, name, current_price, last_updated
Transactions: id, user_id, stock_id, type, quantity, price, total_amount, timestamp
Holdings: id, user_id, stock_id, quantity, avg_purchase_price
```

## � Quick Start (Development)

### Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup MySQL database
mysql -u root -p
CREATE DATABASE portfolio_manager;

# Run Flask app
python app.py
```

### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

## 📈 Analytics Features

### Portfolio Performance

- Total return calculation
- Daily/weekly/monthly performance
- Asset allocation pie charts
- Performance vs market benchmark

### Risk Analysis

- Portfolio volatility
- Sharpe ratio calculation
- Diversification metrics
- Risk-return scatter plots

### Data Visualization

- Interactive charts with Chart.js
- Portfolio composition graphs
- Performance trend lines
- Trading volume analysis

## � Implementation Notes

### Market Data

- Use mock data or free APIs (Alpha Vantage, Yahoo Finance)
- Focus on core functionality over real-time data
- Implement basic stock price simulation for demo

### Python Analytics Integration

- Keep analytics functions within Flask app for simplicity
- Use Pandas for data manipulation and analysis
- Generate charts server-side and send data to frontend

### Frontend Simplicity

- Use React hooks (useState, useEffect) for state management
- Implement simple routing with Next.js app directory
- Focus on functionality over complex UI animations

## 🎯 Success Metrics

### Day 1 Success

- ✅ Flask app running with database connection
- ✅ Basic user working
- ✅ Core models and database schema created

### Day 2 Success

- ✅ Frontend connected to backend APIs
- ✅ Users can buy/sell stocks
- ✅ Portfolio dashboard showing current holdings

### Day 3 Success

- ✅ Analytics dashboard with charts
- ✅ Portfolio performance calculations
- ✅ Demo-ready application

## 🔮 Bonus Features (If Time Allows)

- **Portfolio Rebalancing**: Suggest optimal allocation
- **Watchlist**: Track stocks without buying
- **News Integration**: Basic market news display
- **Export Features**: Download portfolio reports
- **Paper Trading Competition**: Compare team member portfolios

---

**Project Timeline**: 3 Days (Hackathon Style)  
**Team**: Team 02  
**Tech Stack**: Flask + Next.js + Python Analytics  
**Database**: MySQL  
**Focus**: MVP with strong analytics component
