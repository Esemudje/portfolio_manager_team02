import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, DollarSign, PieChart } from 'lucide-react';
import apiService from '../services/apiService';

const Dashboard = () => {
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 0,
    totalCash: 10000, // Starting with $10,000 virtual cash
    totalPL: 0,
    dayChange: 0,
    holdings: []
  });
  const [watchlist] = useState(['AAPL', 'GOOGL', 'AMZN', 'TSLA', 'MSFT']);
  const [stockQuotes, setStockQuotes] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch quotes for watchlist stocks
      const quotes = {};
      for (const symbol of watchlist) {
        try {
          const quote = await apiService.getStockQuote(symbol);
          quotes[symbol] = quote;
        } catch (err) {
          console.warn(`Failed to fetch quote for ${symbol}:`, err);
        }
      }
      
      setStockQuotes(quotes);
      
      // Mock portfolio data - in a real app, this would come from your backend
      const mockHoldings = [
        { symbol: 'AAPL', quantity: 15, averageCost: 193.33, currentPrice: quotes.AAPL?.['05. price'] || 195.60 },
        { symbol: 'GOOGL', quantity: 1, averageCost: 2700.00, currentPrice: quotes.GOOGL?.['05. price'] || 2742.50 },
        { symbol: 'AMZN', quantity: 3, averageCost: 230.00, currentPrice: quotes.AMZN?.['05. price'] || 236.50 }
      ];
      
      const totalValue = mockHoldings.reduce((sum, holding) => 
        sum + (holding.quantity * parseFloat(holding.currentPrice)), 0
      );
      
      const totalCost = mockHoldings.reduce((sum, holding) => 
        sum + (holding.quantity * holding.averageCost), 0
      );
      
      setPortfolioData({
        totalValue,
        totalCash: 10000,
        totalPL: totalValue - totalCost,
        dayChange: 150.25, // Mock day change
        holdings: mockHoldings
      });
      
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercent = (value) => {
    const percent = (value / (portfolioData.totalValue - portfolioData.totalPL)) * 100;
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>
      
      {/* Portfolio Summary */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#667eea' }}>
            {formatCurrency(portfolioData.totalValue + portfolioData.totalCash)}
          </div>
          <div className="stat-label">Total Portfolio Value</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{formatCurrency(portfolioData.totalValue)}</div>
          <div className="stat-label">Invested Value</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{formatCurrency(portfolioData.totalCash)}</div>
          <div className="stat-label">Available Cash</div>
        </div>
        
        <div className="stat-card">
          <div className={`stat-value ${portfolioData.totalPL >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(portfolioData.totalPL)}
          </div>
          <div className="stat-label">
            Total P&L ({formatPercent(portfolioData.totalPL)})
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Current Holdings */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Current Holdings</h2>
            <Link to="/portfolio" className="btn btn-secondary">View All</Link>
          </div>
          
          {portfolioData.holdings.length > 0 ? (
            <div className="table">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Avg Cost</th>
                    <th>Current Price</th>
                    <th>Market Value</th>
                    <th>P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioData.holdings.map((holding, index) => {
                    const marketValue = holding.quantity * parseFloat(holding.currentPrice);
                    const totalCost = holding.quantity * holding.averageCost;
                    const pl = marketValue - totalCost;
                    
                    return (
                      <tr key={index}>
                        <td>
                          <Link to={`/stock/${holding.symbol}`} style={{ color: '#667eea', textDecoration: 'none' }}>
                            <strong>{holding.symbol}</strong>
                          </Link>
                        </td>
                        <td>{holding.quantity}</td>
                        <td>{formatCurrency(holding.averageCost)}</td>
                        <td>{formatCurrency(holding.currentPrice)}</td>
                        <td>{formatCurrency(marketValue)}</td>
                        <td className={pl >= 0 ? 'positive' : 'negative'}>
                          {formatCurrency(pl)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No holdings yet. <Link to="/trading">Start trading</Link> to build your portfolio.</p>
          )}
        </div>

        {/* Watchlist */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Watchlist</h2>
            <Link to="/trading" className="btn btn-primary">Trade</Link>
          </div>
          
          <div className="stock-list">
            {watchlist.map(symbol => {
              const quote = stockQuotes[symbol];
              if (!quote) return null;
              
              const price = parseFloat(quote['05. price'] || 0);
              const change = parseFloat(quote['09. change'] || 0);
              const changePercent = parseFloat(quote['10. change percent']?.replace('%', '') || 0);
              
              return (
                <div key={symbol} className="stock-item">
                  <div className="stock-info">
                    <Link to={`/stock/${symbol}`} style={{ textDecoration: 'none' }}>
                      <div className="stock-symbol">{symbol}</div>
                    </Link>
                  </div>
                  <div className="stock-price">
                    <div className="stock-current-price">
                      {formatCurrency(price)}
                    </div>
                    <div className={`stock-change ${change >= 0 ? 'positive' : 'negative'}`}>
                      {change >= 0 ? '+' : ''}{formatCurrency(change)} ({changePercent.toFixed(2)}%)
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
