import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import apiService from '../services/apiService';

const Portfolio = () => {
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 0,
    totalCash: 10000,
    totalPL: 0,
    holdings: [],
    trades: []
  });
  const [activeTab, setActiveTab] = useState('holdings');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch real data from database
      const [portfolioResponse, tradesResponse, cashResponse] = await Promise.allSettled([
        apiService.getPortfolio(),
        apiService.getTrades(),
        apiService.getBalance()
      ]);

      // Process portfolio holdings
      let holdings = [];
      let totalValue = 0;
      let totalPL = 0;
      
      if (portfolioResponse.status === 'fulfilled' && portfolioResponse.value.holdings) {
        holdings = portfolioResponse.value.holdings.map(holding => ({
          symbol: holding.stock_symbol,
          name: `${holding.stock_symbol} Inc.`, // Could be enhanced with company names
          quantity: parseFloat(holding.quantity),
          averageCost: parseFloat(holding.average_cost),
          currentPrice: parseFloat(holding.average_cost) // Will be updated with current price
        }));
        
        if (portfolioResponse.value.summary) {
          totalValue = portfolioResponse.value.summary.total_portfolio_value || 0;
          totalPL = portfolioResponse.value.summary.total_pnl || 0;
        }
      }

      // Process trades
      let trades = [];
      if (tradesResponse.status === 'fulfilled' && tradesResponse.value.trades) {
        trades = tradesResponse.value.trades.map(trade => ({
          id: trade.trade_id,
          symbol: trade.stock_symbol,
          type: trade.trade_type,
          quantity: parseFloat(trade.quantity),
          price: parseFloat(trade.price_at_trade),
          date: trade.trade_date,
          total: parseFloat(trade.quantity) * parseFloat(trade.price_at_trade)
        }));
      }

      // Get current cash balance
      let cashBalance = 10000; // Default fallback
      if (cashResponse.status === 'fulfilled' && cashResponse.value.cash_balance !== undefined) {
        cashBalance = parseFloat(cashResponse.value.cash_balance);
      }

      // Fetch current market prices for holdings
      for (const holding of holdings) {
        try {
          const quote = await apiService.getStockQuote(holding.symbol);
          if (quote && quote['05. price']) {
            holding.currentPrice = parseFloat(quote['05. price']);
          }
        } catch (err) {
          console.warn(`Failed to fetch current price for ${holding.symbol}:`, err);
        }
      }

      // Recalculate totals with current prices
      if (holdings.length > 0) {
        totalValue = holdings.reduce((sum, holding) => 
          sum + (holding.quantity * holding.currentPrice), 0
        );
        
        const totalCost = holdings.reduce((sum, holding) => 
          sum + (holding.quantity * holding.averageCost), 0
        );
        
        totalPL = totalValue - totalCost;
      }
      
      setPortfolioData({
        totalValue,
        totalCash: cashBalance,
        totalPL,
        holdings,
        trades
      });
      
    } catch (err) {
      setError('Failed to fetch portfolio data');
      console.error('Portfolio error:', err);
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Prepare data for charts
  const pieChartData = portfolioData.holdings.map(holding => ({
    name: holding.symbol,
    value: holding.quantity * holding.currentPrice,
    percentage: ((holding.quantity * holding.currentPrice) / portfolioData.totalValue * 100).toFixed(1)
  }));

  const barChartData = portfolioData.holdings.map(holding => {
    const marketValue = holding.quantity * holding.currentPrice;
    const totalCost = holding.quantity * holding.averageCost;
    const pl = marketValue - totalCost;
    
    return {
      symbol: holding.symbol,
      'Market Value': marketValue,
      'Total Cost': totalCost,
      'P&L': pl
    };
  });

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'];

  if (loading) {
    return <div className="loading">Loading portfolio...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div>
      <h1 className="page-title">Portfolio</h1>
      
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
          <div className="stat-label">Total P&L</div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        <div className="card">
          <h3 className="card-title">Portfolio Allocation</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} (${percentage}%)`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">Holdings Performance</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="symbol" />
                <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Bar dataKey="Market Value" fill="#667eea" />
                <Bar dataKey="Total Cost" fill="#764ba2" />
                <Bar dataKey="P&L" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', borderBottom: '1px solid #e5e7eb' }}>
          <button
            className={`btn ${activeTab === 'holdings' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('holdings')}
          >
            Holdings
          </button>
          <button
            className={`btn ${activeTab === 'trades' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('trades')}
          >
            Trade History
          </button>
        </div>

        {activeTab === 'holdings' && (
          <div>
            <div className="card-header">
              <h3 className="card-title">Current Holdings</h3>
              <Link to="/trading" className="btn btn-success">Add Position</Link>
            </div>
            
            <div className="holdings-table">
              <table className="table">
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Company</th>
                    <th>Quantity</th>
                    <th>Avg Cost</th>
                    <th>Current Price</th>
                    <th>Market Value</th>
                    <th>Total Cost</th>
                    <th>P&L</th>
                    <th>P&L %</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioData.holdings.map((holding, index) => {
                    const marketValue = holding.quantity * holding.currentPrice;
                    const totalCost = holding.quantity * holding.averageCost;
                    const pl = marketValue - totalCost;
                    const plPercent = (pl / totalCost) * 100;
                    
                    return (
                      <tr key={index}>
                        <td>
                          <Link to={`/stock/${holding.symbol}`} style={{ color: '#667eea', textDecoration: 'none' }}>
                            <strong>{holding.symbol}</strong>
                          </Link>
                        </td>
                        <td>{holding.name}</td>
                        <td>{holding.quantity}</td>
                        <td>{formatCurrency(holding.averageCost)}</td>
                        <td>{formatCurrency(holding.currentPrice)}</td>
                        <td><strong>{formatCurrency(marketValue)}</strong></td>
                        <td>{formatCurrency(totalCost)}</td>
                        <td className={pl >= 0 ? 'positive' : 'negative'}>
                          <strong>{formatCurrency(pl)}</strong>
                        </td>
                        <td className={pl >= 0 ? 'positive' : 'negative'}>
                          {plPercent >= 0 ? '+' : ''}{plPercent.toFixed(2)}%
                        </td>
                        <td>
                          <Link to={`/trading?symbol=${holding.symbol}&action=sell`} className="btn btn-danger" style={{ fontSize: '0.8rem', padding: '0.5rem' }}>
                            Sell
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'trades' && (
          <div>
            <h3 className="card-title">Trade History</h3>
            
            <div className="holdings-table">
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Symbol</th>
                    <th>Type</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioData.trades.map((trade) => (
                    <tr key={trade.id}>
                      <td>{formatDate(trade.date)}</td>
                      <td>
                        <Link to={`/stock/${trade.symbol}`} style={{ color: '#667eea', textDecoration: 'none' }}>
                          <strong>{trade.symbol}</strong>
                        </Link>
                      </td>
                      <td>
                        <span className={`btn ${trade.type === 'BUY' ? 'btn-success' : 'btn-danger'}`} style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem' }}>
                          {trade.type}
                        </span>
                      </td>
                      <td>{trade.quantity}</td>
                      <td>{formatCurrency(trade.price)}</td>
                      <td><strong>{formatCurrency(trade.total)}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Portfolio;
