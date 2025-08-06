import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search } from 'lucide-react';
import apiService from '../services/apiService';

const Trading = () => {
  const [searchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStock, setSelectedStock] = useState(null);
  const [stockQuote, setStockQuote] = useState(null);
  const [currentHolding, setCurrentHolding] = useState(null);
  const [tradeAction, setTradeAction] = useState(searchParams.get('action') || 'buy');
  const [quantity, setQuantity] = useState(1);
  const [availableCash, setAvailableCash] = useState(10000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    // Fetch current cash balance
    const fetchCashBalance = async () => {
      try {
        const balance = await apiService.getBalance();
        if (balance.cash_balance !== undefined) {
          setAvailableCash(parseFloat(balance.cash_balance));
        }
      } catch (err) {
        console.warn('Failed to fetch cash balance:', err);
      }
    };
    
    fetchCashBalance();
  }, []);

  // Popular stocks for quick access
  const popularStocks = [
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.' },
    { symbol: 'TSLA', name: 'Tesla Inc.' },
    { symbol: 'MSFT', name: 'Microsoft Corporation' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation' },
    { symbol: 'META', name: 'Meta Platforms Inc.' },
    { symbol: 'NFLX', name: 'Netflix Inc.' }
  ];

  useEffect(() => {
    const symbol = searchParams.get('symbol');
    if (symbol) {
      handleStockSelect(symbol);
    }
  }, [searchParams]);

  const handleStockSelect = async (symbol) => {
    try {
      setLoading(true);
      setError(null);
      setSelectedStock(symbol);
      setCurrentHolding(null); // Reset holding info
      
      // Fetch both stock quote and current holdings
      const [quoteResult, holdingsResult] = await Promise.allSettled([
        apiService.getStockQuote(symbol),
        apiService.getPortfolio(symbol) // Get portfolio data for this specific symbol
      ]);
      
      // Handle quote data
      if (quoteResult.status === 'fulfilled') {
        setStockQuote(quoteResult.value);
      } else {
        // If API fails, try to get cached data from database
        try {
          const cachedQuote = await apiService.getStockQuoteFromDb(symbol);
          if (cachedQuote && !cachedQuote.error) {
            setStockQuote(cachedQuote);
            console.warn(`Using cached data for ${symbol} - API unavailable`);
          } else {
            setError(`No data available for ${symbol} - please try again later`);
          }
        } catch (dbErr) {
          setError(`Failed to fetch data for ${symbol}`);
          console.error('Stock selection error:', quoteResult.reason);
        }
      }
      
      // Handle holdings data
      if (holdingsResult.status === 'fulfilled' && holdingsResult.value.holdings && holdingsResult.value.holdings.length > 0) {
        const holding = holdingsResult.value.holdings[0]; // Should only be one holding for the specific symbol
        setCurrentHolding({
          quantity: parseFloat(holding.quantity || 0),
          averageCost: parseFloat(holding.average_cost || 0),
          marketValue: parseFloat(holding.market_value || 0),
          unrealizedPnl: parseFloat(holding.unrealized_pnl || 0)
        });
      } else {
        setCurrentHolding({ quantity: 0 }); // User doesn't own this stock
      }
      
    } catch (err) {
      setError(`Failed to fetch data for ${symbol}`);
      console.error('Stock selection error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;
    
    await handleStockSelect(searchTerm.toUpperCase());
  };

  const handleTrade = async (e) => {
    e.preventDefault();
    
    if (!selectedStock || !stockQuote || quantity <= 0) {
      setError('Please select a stock and enter a valid quantity');
      return;
    }

    const price = parseFloat(stockQuote['05. price'] || stockQuote.current_price || 0);
    const totalCost = price * quantity;

    if (tradeAction === 'buy' && totalCost > availableCash) {
      setError('Insufficient cash for this trade');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      let result;
      if (tradeAction === 'buy') {
        result = await apiService.buyStock(selectedStock, quantity);
      } else {
        result = await apiService.sellStock(selectedStock, quantity);
      }
      
      // Check if the result indicates success
      if (result.message && result.message.toLowerCase().includes('successful')) {
        setSuccess(result.message);
        
        // Update cash balance after successful trade
        const updatedBalance = await apiService.getBalance();
        if (updatedBalance.cash_balance !== undefined) {
          setAvailableCash(parseFloat(updatedBalance.cash_balance));
        }
        
        setQuantity(1);
      } else {
        // Handle API error response with specific error details
        const errorMessage = result.error || result.message || 'Trade execution failed';
        
        // Check for specific error types and provide user-friendly messages
        if (errorMessage.includes('Insufficient shares')) {
          // Parse the available and requested quantities from the error message
          const availableMatch = errorMessage.match(/Available: ([\d.]+)/);
          const requestedMatch = errorMessage.match(/Requested: ([\d.]+)/);
          
          if (availableMatch && requestedMatch) {
            const available = parseFloat(availableMatch[1]);
            const requested = parseFloat(requestedMatch[1]);
            setError(`Cannot sell ${requested} shares of ${selectedStock}. You only own ${available} shares.`);
          } else {
            setError(`You don't own enough shares of ${selectedStock} to complete this sale.`);
          }
        } else if (errorMessage.includes('Insufficient funds')) {
          setError(`Insufficient cash to buy ${quantity} shares of ${selectedStock}. ${errorMessage}`);
        } else {
          setError(errorMessage);
        }
      }
      
      // Reset success message after 5 seconds
      if (result.message && result.message.toLowerCase().includes('successful')) {
        setTimeout(() => setSuccess(null), 5000);
      }
      
    } catch (err) {
      // Handle errors thrown by the API calls
      let errorMessage = err.message || 'Failed to execute trade';
      
      // Check for specific error patterns and provide user-friendly messages
      if (errorMessage.includes('Insufficient shares')) {
        const availableMatch = errorMessage.match(/Available: ([\d.]+)/);
        const requestedMatch = errorMessage.match(/Requested: ([\d.]+)/);
        
        if (availableMatch && requestedMatch) {
          const available = parseFloat(availableMatch[1]);
          const requested = parseFloat(requestedMatch[1]);
          errorMessage = `Cannot sell ${requested} share(s) of ${selectedStock}. You only own ${available} share(s).`;
        } else {
          errorMessage = `You don't own enough shares of ${selectedStock} to complete this sale.`;
        }
      } else if (errorMessage.includes('Insufficient funds')) {
        errorMessage = `Insufficient cash to buy ${quantity} shares of ${selectedStock}. ${errorMessage}`;
      }
      
      setError(errorMessage);
      console.error('Trade error:', err);
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

  const calculateTotal = () => {
    if (!stockQuote) return 0;
    // Handle both API format ('05. price') and database format ('current_price')
    const price = parseFloat(stockQuote['05. price'] || stockQuote.current_price || 0);
    return price * quantity;
  };

  return (
    <div>
      <h1 className="page-title">Trading</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Stock Search and Selection */}
        <div className="card">
          <h2 className="card-title">Select Stock</h2>
          
          {/* Search */}
          <form onSubmit={handleSearch} className="search-container">
            <div style={{ position: 'relative' }}>
              <Search className="search-icon" size={20} />
              <input
                type="text"
                className="search-input"
                placeholder="Enter stock symbol (e.g., AAPL, GOOGL)"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem' }}>
              Search
            </button>
          </form>

          {/* Popular Stocks */}
          <div style={{ marginTop: '2rem' }}>
            <h3 className="section-title">Popular Stocks</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem' }}>
              {popularStocks.map(stock => (
                <button
                  key={stock.symbol}
                  className={`btn ${selectedStock === stock.symbol ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => handleStockSelect(stock.symbol)}
                  style={{ textAlign: 'left', fontSize: '0.9rem' }}
                >
                  <div><strong>{stock.symbol}</strong></div>
                  <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>{stock.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Selected Stock Info */}
          {selectedStock && stockQuote && (
            <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3>{selectedStock}</h3>
                  <p style={{ color: '#6b7280', margin: 0 }}>
                    {stockQuote['01. symbol'] || stockQuote.symbol} - Last Updated: {stockQuote['07. latest trading day'] || stockQuote.last_updated || 'N/A'}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                    {formatCurrency(stockQuote['05. price'] || stockQuote.current_price)}
                  </div>
                  <div className={parseFloat(stockQuote['09. change'] || stockQuote.change_amount || 0) >= 0 ? 'positive' : 'negative'}>
                    {parseFloat(stockQuote['09. change'] || stockQuote.change_amount || 0) >= 0 ? '+' : ''}
                    {formatCurrency(stockQuote['09. change'] || stockQuote.change_amount || 0)} ({stockQuote['10. change percent'] || stockQuote.change_percent || '0%'})
                  </div>
                </div>
              </div>
              
              {/* Current Holdings Info */}
              {currentHolding !== null && (
                <div style={{ 
                  marginTop: '1rem', 
                  padding: '0.75rem', 
                  backgroundColor: currentHolding.quantity > 0 ? '#f0f9ff' : '#fef2f2', 
                  border: `1px solid ${currentHolding.quantity > 0 ? '#0ea5e9' : '#f87171'}`,
                  borderRadius: '0.375rem'
                }}>
                  <div style={{ fontSize: '0.9rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                    Your Holdings
                  </div>
                  {currentHolding.quantity > 0 ? (
                    <div style={{ fontSize: '0.8rem' }}>
                      <div><strong>{currentHolding.quantity} shares</strong> owned</div>
                      <div>Avg Cost: {formatCurrency(currentHolding.averageCost)}</div>
                      <div>Market Value: {formatCurrency(currentHolding.marketValue)}</div>
                      <div className={currentHolding.unrealizedPnl >= 0 ? 'positive' : 'negative'}>
                        P&L: {formatCurrency(currentHolding.unrealizedPnl)}
                      </div>
                    </div>
                  ) : (
                    <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                      You don't currently own any shares of {selectedStock}
                    </div>
                  )}
                </div>
              )}
              
              <Link to={`/stock/${selectedStock}`} className="btn btn-secondary" style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
                View Details
              </Link>
            </div>
          )}
        </div>

        {/* Trade Form */}
        <div className="card">
          <h2 className="card-title">Place Order</h2>
          
          {!selectedStock && (
            <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
              Select a stock to start trading
            </p>
          )}

          {selectedStock && (
            <form onSubmit={handleTrade} className="trade-form">
              {/* Action Selection */}
              <div className="form-group">
                <label className="form-label">Action</label>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button
                    type="button"
                    className={`btn ${tradeAction === 'buy' ? 'btn-success' : 'btn-secondary'}`}
                    onClick={() => setTradeAction('buy')}
                  >
                    Buy
                  </button>
                  <button
                    type="button"
                    className={`btn ${tradeAction === 'sell' ? 'btn-danger' : 'btn-secondary'}`}
                    onClick={() => setTradeAction('sell')}
                  >
                    Sell
                  </button>
                </div>
              </div>

              {/* Quantity */}
              <div className="form-group">
                <label className="form-label">Quantity</label>
                <div className="quantity-input">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    disabled={quantity <= 1}
                  >
                    -
                  </button>
                  <input
                    type="number"
                    className="form-input"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                    min="1"
                  />
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setQuantity(quantity + 1)}
                  >
                    +
                  </button>
                </div>
                
                {/* Show available shares for sell orders */}
                {tradeAction === 'sell' && currentHolding && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#6b7280' }}>
                    {currentHolding.quantity > 0 ? (
                      <span>Available to sell: <strong>{currentHolding.quantity} shares</strong></span>
                    ) : (
                      <span style={{ color: '#ef4444' }}>⚠️ You don't own any shares of {selectedStock}</span>
                    )}
                  </div>
                )}
              </div>

              {/* Order Type */}
              <div className="form-group">
                <label className="form-label">Order Type</label>
                <select className="form-input">
                  <option value="market">Market Order</option>
                  <option value="limit" disabled>Limit Order (Coming Soon)</option>
                </select>
              </div>

              {/* Trade Summary */}
              {stockQuote && (
                <div className="trade-summary">
                  <h4>Order Summary</h4>
                  <div className="trade-summary-row">
                    <span>Stock:</span>
                    <span>{selectedStock}</span>
                  </div>
                  <div className="trade-summary-row">
                    <span>Action:</span>
                    <span className={tradeAction === 'buy' ? 'positive' : 'negative'}>
                      {tradeAction.toUpperCase()}
                    </span>
                  </div>
                  <div className="trade-summary-row">
                    <span>Quantity:</span>
                    <span>{quantity} shares</span>
                  </div>
                  <div className="trade-summary-row">
                    <span>Price per share:</span>
                    <span>{formatCurrency(stockQuote['05. price'] || stockQuote.current_price)}</span>
                  </div>
                  <div className="trade-summary-row total">
                    <span>Total {tradeAction === 'buy' ? 'Cost' : 'Proceeds'}:</span>
                    <span>{formatCurrency(calculateTotal())}</span>
                  </div>
                  
                  {tradeAction === 'buy' && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#6b7280' }}>
                      Available Cash: {formatCurrency(availableCash)}
                    </div>
                  )}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                className={`btn ${tradeAction === 'buy' ? 'btn-success' : 'btn-danger'}`}
                disabled={loading || !stockQuote}
                style={{ width: '100%', marginTop: '1rem' }}
              >
                {loading ? 'Processing...' : `${tradeAction === 'buy' ? 'Buy' : 'Sell'} ${selectedStock}`}
              </button>
            </form>
          )}
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="error" style={{ marginTop: '1rem' }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ 
          marginTop: '1rem', 
          padding: '1rem', 
          backgroundColor: '#d1fae5', 
          border: '1px solid #10b981', 
          borderRadius: '0.5rem', 
          color: '#065f46' 
        }}>
          {success}
        </div>
      )}
    </div>
  );
};

export default Trading;
