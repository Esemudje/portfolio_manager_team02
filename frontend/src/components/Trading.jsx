import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search, TrendingUp, TrendingDown } from 'lucide-react';
import apiService from '../services/apiService';

const Trading = () => {
  const [searchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStock, setSelectedStock] = useState(null);
  const [stockQuote, setStockQuote] = useState(null);
  const [tradeAction, setTradeAction] = useState(searchParams.get('action') || 'buy');
  const [quantity, setQuantity] = useState(1);
  const [availableCash] = useState(10000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

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
      
      const quote = await apiService.getStockQuote(symbol);
      setStockQuote(quote);
      
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

    const price = parseFloat(stockQuote['05. price'] || 0);
    const totalCost = price * quantity;

    if (tradeAction === 'buy' && totalCost > availableCash) {
      setError('Insufficient cash for this trade');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // In a real app, this would make an API call to your backend to execute the trade
      // For now, we'll simulate a successful trade
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess(`Successfully ${tradeAction === 'buy' ? 'bought' : 'sold'} ${quantity} shares of ${selectedStock} at ${formatCurrency(price)}`);
      setQuantity(1);
      
      // Reset after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      setError('Failed to execute trade');
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
    const price = parseFloat(stockQuote['05. price'] || 0);
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
                    {stockQuote['01. symbol']} - Last Updated: {stockQuote['07. latest trading day']}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                    {formatCurrency(stockQuote['05. price'])}
                  </div>
                  <div className={parseFloat(stockQuote['09. change'] || 0) >= 0 ? 'positive' : 'negative'}>
                    {parseFloat(stockQuote['09. change'] || 0) >= 0 ? '+' : ''}
                    {formatCurrency(stockQuote['09. change'] || 0)} ({stockQuote['10. change percent'] || '0%'})
                  </div>
                </div>
              </div>
              
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
                    <span>{formatCurrency(stockQuote['05. price'])}</span>
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
