import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../services/apiService';
import StockSearchDropdown from './StockSearchDropdown';


const Dashboard = () => {
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 0,
    totalCash: 10000, // Starting with $10,000 virtual cash
    totalPL: 0,
    totalRealizedPL: 0,
    totalUnrealizedPL: 0,
    dayChange: 0,
    holdings: []
  });
  const [isPolling, setIsPolling] = useState(false);
  const [watchlist, setWatchlist] = useState(() => {
    // Load watchlist from localStorage or use default stocks
    const savedWatchlist = localStorage.getItem('portfolioWatchlist');
    return savedWatchlist ? JSON.parse(savedWatchlist) : ['AAPL', 'GOOGL', 'AMZN', 'TSLA', 'MSFT'];
  });
  const [stockQuotes, setStockQuotes] = useState({});
  const [marketNews, setMarketNews] = useState([]);
  const [newsLoading, setNewsLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMarketNews = useCallback(async () => {
  try {
    setNewsLoading(true);

    // Fetch all news articles from the backend
    const news = await apiService.getMarketNews();
    console.log('News data from backend:', news);

    // Randomly shuffle the array and take the first 3
    const shuffled = news.sort(() => 0.5 - Math.random());
    const selected = shuffled.slice(0, 3);

    setMarketNews(
      selected.map((item) => ({
        title: item.headline,
        source: item.reported_by,
        time_published: new Date().toISOString(), // Dummy timestamp
        summary: item.summary || '',
        overall_sentiment_label: item.sentiment || null,
        url: item.url || '#',
        relatedStock: item.related_stock || null
      }))
    );
  } catch (err) {
    console.error('Failed to fetch market news:', err);
  } finally {
    setNewsLoading(false);
  }
}, []);

  // Watchlist management functions
  const addToWatchlist = async (symbol, stockDetails = null) => {
    const upperSymbol = symbol.toUpperCase().trim();
    
    if (!upperSymbol) {
      setError('Please enter a valid stock symbol');
      return;
    }
    
    if (watchlist.includes(upperSymbol)) {
      setError(`${upperSymbol} is already in your watchlist`);
      return;
    }
    
    try {
      // Validate the stock symbol by trying to fetch its quote
      const quote = await apiService.getStockQuote(upperSymbol);
      if (quote && !quote.error) {
        const updatedWatchlist = [...watchlist, upperSymbol];
        setWatchlist(updatedWatchlist);
        localStorage.setItem('portfolioWatchlist', JSON.stringify(updatedWatchlist));
        setError(null);
        
        // Fetch quote for the new stock
        setStockQuotes(prev => ({
          ...prev,
          [upperSymbol]: quote
        }));
        
        // If we have stock details, we could show a success message with company name
        if (stockDetails) {
          console.log(`Added ${stockDetails.name} (${upperSymbol}) to watchlist`);
        }
      } else {
        setError(`Invalid stock symbol: ${upperSymbol}`);
      }
    } catch (err) {
      setError(`Failed to add ${upperSymbol}: Invalid stock symbol`);
    }
  };

  const removeFromWatchlist = (symbol) => {
    const updatedWatchlist = watchlist.filter(s => s !== symbol);
    setWatchlist(updatedWatchlist);
    localStorage.setItem('portfolioWatchlist', JSON.stringify(updatedWatchlist));
    
    // Remove from stock quotes
    setStockQuotes(prev => {
      const newQuotes = { ...prev };
      delete newQuotes[symbol];
      return newQuotes;
    });
  };


  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch real portfolio data and comprehensive P&L data from database
      const [portfolioResponse, cashResponse, comprehensivePnLResponse] = await Promise.allSettled([
        apiService.getPortfolio(),
        apiService.getBalance(),
        apiService.getComprehensivePnL() // Get comprehensive P&L (realized + unrealized) for all holdings
      ]);

      // Get portfolio data
      let holdings = [];
      let totalValue = 0;
      let totalPL = 0;
      let totalRealizedPL = 0;
      let totalUnrealizedPL = 0;
      
      // Get comprehensive P&L data by symbol for mapping
      let comprehensivePnLBySymbol = {};
      if (comprehensivePnLResponse.status === 'fulfilled' && comprehensivePnLResponse.value) {
        const pnlData = comprehensivePnLResponse.value;
        
        // Extract totals from summary
        if (pnlData.summary) {
          totalRealizedPL = parseFloat(
            pnlData.summary.total_realized_pnl || 
            pnlData.summary.realized_pnl || 
            0
          );
          totalUnrealizedPL = parseFloat(
            pnlData.summary.total_unrealized_pnl || 
            pnlData.summary.unrealized_pnl || 
            0
          );
        }
        
        // Extract per-symbol data from unrealized holdings
        if (pnlData.unrealized && pnlData.unrealized.holdings) {
          pnlData.unrealized.holdings.forEach(item => {
            comprehensivePnLBySymbol[item.symbol] = {
              realizedPnl: 0, // Realized PnL is per-stock specific, not available in current structure
              unrealizedPnl: parseFloat(item.unrealized_pnl || 0),
              totalPnl: parseFloat(item.unrealized_pnl || 0), // For now, only unrealized available per-stock
              totalReturn: 0,
              totalReturnPercent: parseFloat(item.unrealized_pnl_percent || 0)
            };
          });
        }
      }
      
      if (portfolioResponse.status === 'fulfilled' && portfolioResponse.value.holdings) {
        holdings = portfolioResponse.value.holdings.map(holding => {
          const comprehensivePnL = comprehensivePnLBySymbol[holding.stock_symbol] || {};
          return {
            symbol: holding.stock_symbol,
            quantity: parseFloat(holding.quantity),
            averageCost: parseFloat(holding.average_cost),
            currentPrice: parseFloat(holding.current_price || holding.average_cost), // Use database current price
            marketValue: parseFloat(holding.market_value || 0),
            unrealizedPnl: comprehensivePnL.unrealizedPnl || parseFloat(holding.unrealized_pnl || 0),
            realizedPnl: comprehensivePnL.realizedPnl || 0,
            totalPnl: comprehensivePnL.totalPnl || 0,
            totalReturn: comprehensivePnL.totalReturn || 0,
            totalReturnPercent: comprehensivePnL.totalReturnPercent || 0
          };
        });
        
        if (portfolioResponse.value.summary) {
          totalValue = portfolioResponse.value.summary.total_portfolio_value || 0;
          totalPL = portfolioResponse.value.summary.total_pnl || 0;
        }
      }

      // Get current cash balance
      let cashBalance = 10000; // Default fallback
      if (cashResponse.status === 'fulfilled' && cashResponse.value.cash_balance !== undefined) {
        cashBalance = parseFloat(cashResponse.value.cash_balance);
      }

      // Fetch quotes for watchlist stocks and holdings with intelligent caching
      // First try database-only, then fallback to API if needed
      const quotes = {};
      const allSymbols = [...new Set([...watchlist, ...holdings.map(h => h.symbol)])]; // Combine and deduplicate
      
      for (const symbol of allSymbols) {
        try {
          // Use database-first approach (backend automatically handles this)
          const quote = await apiService.getStockQuote(symbol);
          quotes[symbol] = quote;
        } catch (err) {
          console.warn(`Failed to fetch quote for ${symbol}:`, err);
          // Optionally try to get from database only as fallback
          try {
            const dbQuote = await apiService.getStockQuoteFromDb(symbol);
            if (dbQuote && !dbQuote.error) {
              quotes[symbol] = dbQuote;
            }
          } catch (dbErr) {
            console.warn(`No cached data available for ${symbol}`);
          }
        }
      }
      
      setStockQuotes(quotes);
      setPortfolioData({
        totalValue,
        totalCash: cashBalance,
        totalPL,
        totalRealizedPL,
        totalUnrealizedPL,
        dayChange: 0, // Could be calculated from daily performance
        holdings
      });

      // Fetch market news from top watchlist stocks
      fetchMarketNews();
      
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  }, [watchlist, fetchMarketNews]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Add polling for real-time updates (numbers only, no UI disruption)
  useEffect(() => {
    const POLLING_INTERVAL = 30000; // 30 seconds
    
    const intervalId = setInterval(async () => {
      console.log('Polling dashboard data...');
      setIsPolling(true);
      
      try {
        // Fetch only the essential data without triggering loading state
        const [portfolioResponse, cashResponse, comprehensivePnLResponse] = await Promise.allSettled([
          apiService.getPortfolio(),
          apiService.getBalance(),
          apiService.getComprehensivePnL()
        ]);

        // Update portfolio data
        let holdings = [];
        let totalValue = 0;
        let totalPL = 0;
        let totalRealizedPL = 0;
        let totalUnrealizedPL = 0;
        
        // Get comprehensive P&L data
        let comprehensivePnLBySymbol = {};
        if (comprehensivePnLResponse.status === 'fulfilled' && comprehensivePnLResponse.value) {
          const pnlData = comprehensivePnLResponse.value;
          console.log('Polling - P&L data structure:', pnlData);
          
          if (pnlData.summary) {
            console.log('Polling - P&L summary:', pnlData.summary);
            totalRealizedPL = parseFloat(
              pnlData.summary.total_realized_pnl || 
              pnlData.summary.realized_pnl || 
              0
            );
            totalUnrealizedPL = parseFloat(
              pnlData.summary.total_unrealized_pnl || 
              pnlData.summary.unrealized_pnl || 
              0
            );
            totalPL = totalRealizedPL + totalUnrealizedPL;
            console.log('Polling - Calculated P&L:', { totalRealizedPL, totalUnrealizedPL, totalPL });
          }

          if (pnlData.by_symbol) {
            pnlData.by_symbol.forEach(item => {
              comprehensivePnLBySymbol[item.symbol] = item;
            });
          }
        }

        if (portfolioResponse.status === 'fulfilled' && portfolioResponse.value) {
          const data = portfolioResponse.value;
          
          if (data.holdings && Array.isArray(data.holdings)) {
            holdings = data.holdings.map(holding => ({
              symbol: holding.symbol || holding.stock_symbol, // Handle both formats
              quantity: parseFloat(holding.quantity || 0),
              averageCost: parseFloat(holding.average_cost || 0),
              currentPrice: parseFloat(holding.current_price || 0),
              marketValue: parseFloat(holding.market_value || 0),
              costBasis: parseFloat(holding.cost_basis || 0),
              unrealizedPnl: parseFloat(holding.unrealized_pnl || 0),
              realizedPnl: comprehensivePnLBySymbol[holding.symbol || holding.stock_symbol]?.realized_pnl || 0
            }));
            
            // Calculate total value from holdings if summary not available
            totalValue = holdings.reduce((sum, holding) => sum + holding.marketValue, 0);
            
            // Calculate P&L totals from holdings if not available from summary
            if (totalRealizedPL === 0 && totalUnrealizedPL === 0) {
              totalUnrealizedPL = holdings.reduce((sum, holding) => sum + holding.unrealizedPnl, 0);
              totalRealizedPL = holdings.reduce((sum, holding) => sum + (holding.realizedPnl || 0), 0);
              totalPL = totalRealizedPL + totalUnrealizedPL;
            }
          }
          
          // Use summary if available, otherwise use calculated value
          if (data.summary) {
            totalValue = parseFloat(data.summary.total_portfolio_value || data.summary.total_value || totalValue);
            totalPL = parseFloat(data.summary.total_pnl || totalPL);
          }
        }

        let cashBalance = 10000;
        if (cashResponse.status === 'fulfilled' && cashResponse.value?.cash_balance !== undefined) {
          cashBalance = parseFloat(cashResponse.value.cash_balance);
        }

        // Update watchlist quotes and holdings quotes
        const quotes = {};
        const allSymbols = [...new Set([...watchlist, ...holdings.map(h => h.symbol)])]; // Combine and deduplicate
        
        for (const symbol of allSymbols) {
          try {
            const quote = await apiService.getStockQuote(symbol);
            quotes[symbol] = quote;
          } catch (err) {
            console.warn(`Failed to fetch quote for ${symbol}:`, err);
          }
        }

        // Update state without triggering loading
        setStockQuotes(quotes);
        setPortfolioData({
          totalValue,
          totalCash: cashBalance,
          totalPL,
          totalRealizedPL,
          totalUnrealizedPL,
          dayChange: 0,
          holdings
        });

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
  }, [watchlist]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

const DarkModeToggle = () => {
  const [darkMode, setDarkMode] = useState(() => {
    // Read initial value from localStorage
    return localStorage.getItem('darkMode') === 'true';
  });

  useEffect(() => {
    document.body.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);


    const toggleDarkMode = () => {
      setDarkMode(!darkMode); //actually toggles the state
  }
  return (
    <div className="dark-mode-toggle">
      <label className="switch">
        <input type="checkbox" checked={darkMode} onChange={toggleDarkMode} />
        <span className="slider"></span>
      </label>
      <span className='darkmode'> Dark Mode</span>
    </div>
  );

  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
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
        <h1 className="page-title" style={{ margin: 0 }}>Dashboard</h1>
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



<div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
  <DarkModeToggle />
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
          <br></br>
          <Link to='/cash' className="btn btn-primary">Manage cash</Link>
        </div>
        
        <div className="stat-card">
          <div className={`stat-value ${portfolioData.totalPL >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(portfolioData.totalPL)}
          </div>
          <div className="stat-label">Total P&L</div>
          {portfolioData.totalRealizedPL !== undefined && portfolioData.totalUnrealizedPL !== undefined && (
            <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#6b7280' }}>
              <div className={portfolioData.totalUnrealizedPL >= 0 ? 'positive' : 'negative'}>
                Unrealized: {formatCurrency(portfolioData.totalUnrealizedPL)}
              </div>
              <div className={portfolioData.totalRealizedPL >= 0 ? 'positive' : 'negative'}>
                Realized: {formatCurrency(portfolioData.totalRealizedPL)}
              </div>
            </div>
          )}
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
                    <th>Change</th>
                    <th>Change %</th>
                    <th>Market Value</th>
                    <th>P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioData.holdings.map((holding, index) => {
                    // Use fresh stock quote if available, otherwise fall back to database price
                    const freshQuote = stockQuotes[holding.symbol];
                    const currentPrice = freshQuote ? 
                      parseFloat(freshQuote['05. price'] || freshQuote.current_price || holding.currentPrice) : 
                      holding.currentPrice;
                    
                    // Use pre-calculated values from database
                    const marketValue = holding.marketValue;
                    const pl = holding.unrealizedPnl;
                    
                    // Calculate change amount and percentage using fresh price
                    const changeAmount = currentPrice - holding.averageCost;
                    const changePercent = holding.averageCost > 0 ? ((changeAmount / holding.averageCost) * 100) : 0;
                    
                    return (
                      <tr key={index}>
                        <td>
                          <Link to={`/stock/${holding.symbol}`} style={{ color: '#667eea', textDecoration: 'none' }}>
                            <strong>{holding.symbol}</strong>
                          </Link>
                        </td>
                        <td>{holding.quantity}</td>
                        <td>{formatCurrency(holding.averageCost)}</td>
                        <td>{formatCurrency(currentPrice)}</td>
                        <td className={changeAmount >= 0 ? 'positive' : 'negative'}>
                          {changeAmount >= 0 ? '+' : ''}{formatCurrency(changeAmount)}
                        </td>
                        <td className={changePercent >= 0 ? 'positive' : 'negative'}>
                          {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
                        </td>
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
          
          {/* Add Stock Form with Enhanced Search */}
          <div style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb' }}>
            <StockSearchDropdown 
              onStockSelect={addToWatchlist}
              className="watchlist-search"
            />
          </div>
          
          <div className="stock-list">
            {watchlist.length > 0 ? (
              watchlist.map(symbol => {
                const quote = stockQuotes[symbol];
                if (!quote) return null;
                
                // Handle both API format and database format
                const price = parseFloat(quote['05. price'] || quote.current_price || 0);
                const change = parseFloat(quote['09. change'] || quote.change_amount || 0);
                const changePercent = parseFloat(quote['10. change percent']?.replace('%', '') || quote.change_percent?.replace('%', '') || 0);
                
                return (
                  <div key={symbol} className="stock-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', flex: 1 }}>
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
                    <button
                      onClick={() => removeFromWatchlist(symbol)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#ef4444',
                        cursor: 'pointer',
                        fontSize: '1.2rem',
                        padding: '0.25rem',
                        marginLeft: '0.5rem'
                      }}
                      title={`Remove ${symbol} from watchlist`}
                    >
                      ×
                    </button>
                  </div>
                );
              })
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                Your watchlist is empty. Add some stocks to get started!
              </div>
            )}
          </div>
        </div>
      </div>
      

      {/* Market News Section */}
      <div className="card" style={{ marginTop: '2rem' }}>
        <div className="card-header">
          <h2 className="card-title">Market News</h2>
          <button 
            onClick={fetchMarketNews} 
            className="btn btn-secondary"
            disabled={newsLoading}
          >
            {newsLoading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
        
        {newsLoading ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
            Loading market news...
          </div>
        ) : marketNews.length > 0 ? (
          <div style={{ display: 'grid', gap: '1.5rem', padding: '1rem' }}>
            {marketNews.map((article, index) => (
              <div key={index} style={{ 
                padding: '1.5rem', 
                border: '1px solid #e5e7eb', 
                borderRadius: '0.5rem',
                backgroundColor: '#fafafa'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <h4 style={{ marginBottom: '0.5rem', flex: 1 }}>
                    <a 
                      href={article.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ color: '#667eea', textDecoration: 'none' }}
                    >
                      {article.title}
                    </a>
                  </h4>
                  {article.relatedStock && (
                    <Link 
                      to={`/stock/${article.relatedStock}`}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem', marginLeft: '1rem' }}
                    >
                      {article.relatedStock}
                    </Link>
                  )}
                </div>
                <p style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                  {article.source} • {new Date(article.time_published).toLocaleDateString()}
                </p>
                <p style={{ color: '#374151', lineHeight: '1.6' }}>
                  {article.summary}
                </p>
                {article.overall_sentiment_label && (
                  <span 
                    className={`btn ${
                      article.overall_sentiment_label === 'Positive' ? 'btn-success' : 
                      article.overall_sentiment_label === 'Negative' ? 'btn-danger' : 
                      'btn-secondary'
                    }`}
                    style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem', marginTop: '0.5rem' }}
                  >
                    {article.overall_sentiment_label} Sentiment
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p style={{ textAlign: 'center', color: '#6b7280', padding: '2rem' }}>
            No market news available. Click refresh to try again.
          </p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;