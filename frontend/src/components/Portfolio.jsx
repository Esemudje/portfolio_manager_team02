import React, { useState, useEffect, useCallback } from 'react';
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
  const [comprehensivePnL, setComprehensivePnL] = useState({
    realizedPnL: 0,
    unrealizedPnL: 0,
    totalPnL: 0
  });
  const [isPolling, setIsPolling] = useState(false);
  const [activeTab, setActiveTab] = useState('holdings');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Normalize trade from API into UI-friendly shape
  const mapTrade = useCallback((trade) => ({
    id: trade.trade_id,
    symbol: trade.stock_symbol,
    type: trade.trade_type,
    quantity: Number(trade.quantity || 0),
    price: Number(trade.price_at_trade || 0),
    date: trade.trade_date,
    total: Number(trade.quantity || 0) * Number(trade.price_at_trade || 0)
  }), []);

  const fetchPortfolioData = useCallback(async (isPolling = false) => {
    try {
      // Only show loading spinner if not polling (initial load or manual refresh)
      if (!isPolling) {
        setLoading(true);
      }
      setError(null);
      
      // Fetch real data from database - this already includes calculated P&L and current prices
      // No additional API calls needed as backend provides comprehensive portfolio data
      const [portfolioResponse, tradesResponse, cashResponse, comprehensivePnLResponse] = await Promise.allSettled([
        apiService.getPortfolio(),
        apiService.getTrades(),
        apiService.getBalance(),
        apiService.getComprehensivePnL()
      ]);

      // Process portfolio holdings - all data comes from database with pre-calculated values
      let holdings = [];
      let totalValue = 0;
      
      if (portfolioResponse.status === 'fulfilled' && portfolioResponse.value.holdings) {
        holdings = portfolioResponse.value.holdings.map(holding => ({
          symbol: holding.stock_symbol || holding.symbol, // Handle both formats
          name: `${holding.stock_symbol || holding.symbol} Inc.`, // Could be enhanced with company names from database
          quantity: parseFloat(holding.quantity),
          averageCost: parseFloat(holding.average_cost),
          currentPrice: parseFloat(holding.current_price || holding.average_cost), // From database cache
          marketValue: parseFloat(holding.market_value || 0), // Pre-calculated by backend
          costBasis: parseFloat(holding.cost_basis || 0), // Pre-calculated by backend  
          unrealizedPnl: parseFloat(holding.unrealized_pnl || 0) // Pre-calculated by backend
        }));
        
        if (portfolioResponse.value.summary) {
          totalValue = portfolioResponse.value.summary.total_portfolio_value || 0;
        }
      }

      // Process trades - all from database, no API calls needed
      let trades = [];
      if (tradesResponse.status === 'fulfilled' && tradesResponse.value.trades) {
        trades = tradesResponse.value.trades.map(mapTrade);
      }

      // Get current cash balance
      let cashBalance = 10000; // Default fallback
      if (cashResponse.status === 'fulfilled' && cashResponse.value.cash_balance !== undefined) {
        cashBalance = parseFloat(cashResponse.value.cash_balance);
      }

      // Process comprehensive P&L data
      let comprehensivePnLData = {
        realizedPnL: 0,
        unrealizedPnL: 0,
        totalPnL: 0
      };
      
      if (comprehensivePnLResponse.status === 'fulfilled' && comprehensivePnLResponse.value) {
        const pnlData = comprehensivePnLResponse.value;
        comprehensivePnLData = {
          realizedPnL: parseFloat(pnlData.summary?.realized_pnl || 0),
          unrealizedPnL: parseFloat(pnlData.summary?.unrealized_pnl || 0),
          totalPnL: parseFloat(pnlData.summary?.total_pnl || 0)
        };
        setComprehensivePnL(comprehensivePnLData);
      }

      // Portfolio data is already calculated by backend with current market prices
      setPortfolioData({
        totalValue,
        totalCash: cashBalance,
        totalPL: comprehensivePnLData.totalPnL, // Use consistent P&L source
        holdings,
        trades
      });
      
    } catch (err) {
      setError('Failed to fetch portfolio data');
      console.error('Portfolio error:', err);
    } finally {
      setLoading(false);
    }
  }, [mapTrade]);

  useEffect(() => {
    fetchPortfolioData();
  }, [fetchPortfolioData]);

  // Add polling for real-time updates (numbers only, no UI disruption)
  useEffect(() => {
    const POLLING_INTERVAL = 30000; // 30 seconds
    
    const intervalId = setInterval(async () => {
      console.log('Polling portfolio data...');
      setIsPolling(true);
      
      try {
        const [portfolioResponse, tradesResponse, cashResponse, comprehensivePnLResponse] = await Promise.allSettled([
          apiService.getPortfolio(),
          apiService.getTrades(),
          apiService.getBalance(),
          apiService.getComprehensivePnL()
        ]);

        // Process portfolio data
        let totalValue = 0;
        let holdings = [];
        let trades = [];
        
        if (portfolioResponse.status === 'fulfilled' && portfolioResponse.value) {
          const data = portfolioResponse.value;
          
          if (data.holdings && Array.isArray(data.holdings)) {
            holdings = data.holdings.map(holding => ({
              symbol: holding.symbol || holding.stock_symbol, // Handle both formats
              name: `${holding.stock_symbol || holding.symbol} Inc.`, // Consistent with initial fetch
              quantity: parseFloat(holding.quantity || 0),
              averageCost: parseFloat(holding.average_cost || 0),
              currentPrice: parseFloat(holding.current_price || 0),
              marketValue: parseFloat(holding.market_value || 0),
              costBasis: parseFloat(holding.cost_basis || 0),
              unrealizedPnl: parseFloat(holding.unrealized_pnl || 0)
            }));
            
            // Calculate total value from holdings if summary not available
            totalValue = holdings.reduce((sum, holding) => sum + holding.marketValue, 0);
          }
          
          // Use summary if available, otherwise use calculated value
          if (data.summary) {
            totalValue = parseFloat(data.summary.total_portfolio_value || data.summary.total_value || totalValue);
          }
        }

        if (tradesResponse.status === 'fulfilled' && tradesResponse.value?.trades) {
          // Normalize trades during polling as well
          trades = tradesResponse.value.trades.map(mapTrade);
        }

        let cashBalance = 10000;
        if (cashResponse.status === 'fulfilled' && cashResponse.value?.cash_balance !== undefined) {
          cashBalance = parseFloat(cashResponse.value.cash_balance);
        }

        // Process comprehensive P&L
        let comprehensivePnLData = {
          realizedPnL: 0,
          unrealizedPnL: 0,
          totalPnL: 0
        };

        if (comprehensivePnLResponse.status === 'fulfilled' && comprehensivePnLResponse.value?.summary) {
          const summary = comprehensivePnLResponse.value.summary;
          comprehensivePnLData = {
            realizedPnL: parseFloat(summary.realized_pnl || 0),
            unrealizedPnL: parseFloat(summary.unrealized_pnl || 0),
            totalPnL: parseFloat(summary.total_pnl || 0)
          };
        }

        // Update state without triggering loading
        setPortfolioData({
          totalValue,
          totalCash: cashBalance,
          totalPL: comprehensivePnLData.totalPnL,
          holdings,
          trades
        });
        setComprehensivePnL(comprehensivePnLData);

      } catch (err) {
        console.warn('Polling failed:', err);
      } finally {
        setIsPolling(false);
      }
    }, POLLING_INTERVAL);

    // Cleanup interval on component unmount
    return () => {
      clearInterval(intervalId);
    };
  }, [mapTrade]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  // Robust date parsing for non-ISO strings like 'YYYY-MM-DD HH:mm:ss'
  const parseDateSafe = (dateString) => {
    if (!dateString) return null;
    const direct = new Date(dateString);
    if (!isNaN(direct.getTime())) return direct;
    const iso = new Date((dateString || '').replace(' ', 'T'));
    if (!isNaN(iso.getTime())) return iso;
    const isoZ = new Date(((dateString || '').replace(' ', 'T')) + 'Z');
    if (!isNaN(isoZ.getTime())) return isoZ;
    return null;
  };

  const formatDate = (dateString) => {
    const d = parseDateSafe(dateString);
    if (!d) return '—';
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  // Prepare data for charts using database values
  const pieChartData = portfolioData.holdings.map(holding => ({
    name: holding.symbol,
    value: holding.marketValue,
    percentage: ((holding.marketValue) / portfolioData.totalValue * 100).toFixed(1)
  }));

  const barChartData = portfolioData.holdings.map(holding => ({
    symbol: holding.symbol,
    'Market Value': holding.marketValue,
    'Total Cost': holding.costBasis,
    'P&L': holding.unrealizedPnl
  }));

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'];

  if (loading) {
    return <div className="loading">Loading portfolio...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div>
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 className="page-title" style={{ margin: 0 }}>Portfolio</h1>
        {isPolling && (
          <div style={{ 
            fontSize: '0.8rem', 
            color: '#10b981', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.5rem' 
          }}>
            <div style={{ 
              width: '12px', 
              height: '12px', 
              border: '2px solid #e5e7eb', 
              borderTop: '2px solid #10b981', 
              borderRadius: '50%', 
              animation: 'spin 1s linear infinite' 
            }}></div>
            Updating data...
          </div>
        )}
      </div>
      
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
          <div className={`stat-value ${comprehensivePnL.totalPnL >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(comprehensivePnL.totalPnL)}
          </div>
          <div className="stat-label">Total P&L</div>
          <div style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
            <div style={{ color: comprehensivePnL.unrealizedPnL >= 0 ? '#10b981' : '#ef4444' }}>
              Unrealized: {formatCurrency(comprehensivePnL.unrealizedPnL)}
            </div>
            <div style={{ color: comprehensivePnL.realizedPnL >= 0 ? '#10b981' : '#ef4444' }}>
              Realized: {formatCurrency(comprehensivePnL.realizedPnL)}
            </div>
          </div>
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
                    // Use pre-calculated values from database
                    const marketValue = holding.marketValue;
                    const totalCost = holding.costBasis;
                    const pl = holding.unrealizedPnl;
                    const plPercent = totalCost > 0 ? (pl / totalCost) * 100 : 0;
                    
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
