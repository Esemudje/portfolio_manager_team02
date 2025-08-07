import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Clock, X, TrendingUp, TrendingDown } from 'lucide-react';
import apiService from '../services/apiService';
import StockSearchDropdown from './StockSearchDropdown';

const EnhancedTrading = () => {
  const [searchParams] = useSearchParams();
  const [selectedStock, setSelectedStock] = useState(null);
  const [stockQuote, setStockQuote] = useState(null);
  const [currentHolding, setCurrentHolding] = useState(null);
  const [orderSide, setOrderSide] = useState(searchParams.get('action') || 'buy');
  const [orderType, setOrderType] = useState('market');
  const [quantity, setQuantity] = useState(1);
  const [price, setPrice] = useState('');
  const [stopPrice, setStopPrice] = useState('');
  const [limitPrice, setLimitPrice] = useState('');
  const [availableCash, setAvailableCash] = useState(10000);
  const [pendingOrders, setPendingOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Order type definitions
  const orderTypes = {
    market: {
      name: 'Market Order',
      description: 'Buy/sell immediately at current market price',
      fields: []
    },
    limit: {
      name: 'Limit Order',
      description: 'Buy/sell only at specified price or better',
      fields: ['price']
    },
    stop: {
      name: 'Stop Order',
      description: 'Trigger market order when stop price is reached',
      fields: ['stopPrice']
    },
    stop_limit: {
      name: 'Stop-Limit Order',
      description: 'Trigger limit order when stop price is reached',
      fields: ['stopPrice', 'limitPrice']
    }
  };

  useEffect(() => {
    fetchCashBalance();
    fetchPendingOrders();
  }, []);

  useEffect(() => {
    if (selectedStock) {
      fetchPendingOrders(selectedStock);
    }
  }, [selectedStock]);

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

  const fetchPendingOrders = async (symbol = null) => {
    try {
      const result = await apiService.getPendingOrders('default_user', symbol);
      setPendingOrders(result.orders || []);
    } catch (err) {
      console.warn('Failed to fetch pending orders:', err);
    }
  };

  const handleStockSelect = async (symbol) => {
    try {
      setSelectedStock(symbol);
      setError(null);
      setSuccess(null);
      
      const [quoteResult, holdingsResult] = await Promise.allSettled([
        apiService.getStockQuote(symbol),
        apiService.getPortfolio(symbol)
      ]);

      if (quoteResult.status === 'fulfilled') {
        setStockQuote(quoteResult.value);
        
        // Auto-fill price fields based on current price
        const currentPrice = parseFloat(quoteResult.value['05. price'] || quoteResult.value.current_price || 0);
        if (currentPrice > 0) {
          setPrice(currentPrice.toFixed(2));
          setStopPrice(currentPrice.toFixed(2));
          setLimitPrice(currentPrice.toFixed(2));
        }
      }

      if (holdingsResult.status === 'fulfilled' && holdingsResult.value.holdings && holdingsResult.value.holdings.length > 0) {
        const holding = holdingsResult.value.holdings[0];
        setCurrentHolding({
          quantity: parseFloat(holding.quantity || 0),
          averageCost: parseFloat(holding.average_cost || 0),
          marketValue: parseFloat(holding.market_value || 0),
          unrealizedPnl: parseFloat(holding.unrealized_pnl || 0)
        });
      } else {
        setCurrentHolding({ quantity: 0 });
      }
      
      // Fetch pending orders for this stock
      fetchPendingOrders(symbol);
      
    } catch (err) {
      setError(`Failed to fetch data for ${symbol}: ${err.message}`);
    }
  };

  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    
    if (!selectedStock || !stockQuote || quantity <= 0) {
      setError('Please select a stock and enter a valid quantity');
      return;
    }

    // Validate required fields based on order type
    const requiredFields = orderTypes[orderType].fields;
    for (const field of requiredFields) {
      if (field === 'price' && !price) {
        setError('Price is required for limit orders');
        return;
      }
      if (field === 'stopPrice' && !stopPrice) {
        setError('Stop price is required for stop orders');
        return;
      }
      if (field === 'limitPrice' && !limitPrice) {
        setError('Limit price is required for stop-limit orders');
        return;
      }
    }

    // Additional validations
    const currentPrice = parseFloat(stockQuote['05. price'] || stockQuote.current_price || 0);
    
    if (orderType === 'market' && orderSide === 'buy') {
      const totalCost = currentPrice * quantity;
      if (totalCost > availableCash) {
        setError('Insufficient cash for this trade');
        return;
      }
    }

    if (orderSide === 'sell' && currentHolding && quantity > currentHolding.quantity) {
      setError(`Cannot sell ${quantity} shares. You only own ${currentHolding.quantity} shares.`);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const orderData = {
        symbol: selectedStock,
        side: orderSide,
        quantity: quantity,
        orderType: orderType,
        price: price ? parseFloat(price) : null,
        stopPrice: stopPrice ? parseFloat(stopPrice) : null,
        limitPrice: limitPrice ? parseFloat(limitPrice) : null
      };
      
      const result = await apiService.placeOrder(orderData);
      
      if (result.success) {
        setSuccess(result.message);
        
        // Reset form
        setQuantity(1);
        
        // Refresh data
        await Promise.all([
          fetchCashBalance(),
          fetchPendingOrders(selectedStock),
          handleStockSelect(selectedStock) // Refresh holdings
        ]);
        
        // Clear success message after 5 seconds
        setTimeout(() => setSuccess(null), 5000);
      } else {
        setError(result.message || 'Order placement failed');
      }
      
    } catch (err) {
      setError(`Failed to place order: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOrder = async (orderId) => {
    try {
      const result = await apiService.cancelOrder(orderId);
      if (result.success) {
        setSuccess('Order cancelled successfully');
        fetchPendingOrders(selectedStock);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(result.message || 'Failed to cancel order');
      }
    } catch (err) {
      setError(`Failed to cancel order: ${err.message}`);
    }
  };

  const calculateOrderValue = () => {
    if (!stockQuote || quantity <= 0) return 0;
    
    const currentPrice = parseFloat(stockQuote['05. price'] || stockQuote.current_price || 0);
    let orderPrice = currentPrice;
    
    if (orderType === 'limit' && price) {
      orderPrice = parseFloat(price);
    } else if (orderType === 'stop_limit' && limitPrice) {
      orderPrice = parseFloat(limitPrice);
    }
    
    return orderPrice * quantity;
  };

  const renderOrderTypeFields = () => {
    const fields = orderTypes[orderType].fields;
    
    return fields.map(field => {
      switch (field) {
        case 'price':
          return (
            <div key="price" className="form-group">
              <label>Limit Price ($)</label>
              <input
                type="number"
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="form-control"
                placeholder="Enter limit price"
                required
              />
              <small className="form-text text-muted">
                {orderSide === 'buy' ? 'Maximum price to pay' : 'Minimum price to accept'}
              </small>
            </div>
          );
        case 'stopPrice':
          return (
            <div key="stopPrice" className="form-group">
              <label>Stop Price ($)</label>
              <input
                type="number"
                step="0.01"
                value={stopPrice}
                onChange={(e) => setStopPrice(e.target.value)}
                className="form-control"
                placeholder="Enter stop price"
                required
              />
              <small className="form-text text-muted">
                Order triggers when price {orderSide === 'buy' ? 'reaches or exceeds' : 'reaches or falls below'} this level
              </small>
            </div>
          );
        case 'limitPrice':
          return (
            <div key="limitPrice" className="form-group">
              <label>Limit Price ($)</label>
              <input
                type="number"
                step="0.01"
                value={limitPrice}
                onChange={(e) => setLimitPrice(e.target.value)}
                className="form-control"
                placeholder="Enter limit price"
                required
              />
              <small className="form-text text-muted">
                After stop triggers, order becomes limit order at this price
              </small>
            </div>
          );
        default:
          return null;
      }
    });
  };

  return (
    <div className="trading-container">
      <div className="row">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              <h3>Enhanced Trading</h3>
              <p className="text-muted">Place market, limit, stop, and stop-limit orders</p>
            </div>
            <div className="card-body">
              {/* Stock Search */}
              <div className="search-section mb-4">
                <h5>Search Stock</h5>
                <StockSearchDropdown
                  onStockSelect={handleStockSelect}
                  placeholder="Search by company name or symbol..."
                />
              </div>

              {/* Selected Stock Info */}
              {selectedStock && stockQuote && (
                <div className="stock-info mb-4">
                  <div className="row">
                    <div className="col-md-6">
                      <h4>{selectedStock}</h4>
                      <p className="current-price">
                        Current Price: <strong>${parseFloat(stockQuote['05. price'] || stockQuote.current_price || 0).toFixed(2)}</strong>
                      </p>
                    </div>
                    <div className="col-md-6">
                      {currentHolding && currentHolding.quantity > 0 && (
                        <div className="holdings-info">
                          <p><strong>Your Holdings:</strong></p>
                          <p>Shares: {currentHolding.quantity}</p>
                          <p>Avg Cost: ${currentHolding.averageCost.toFixed(2)}</p>
                          <p className={currentHolding.unrealizedPnl >= 0 ? 'positive' : 'negative'}>
                            P&L: ${currentHolding.unrealizedPnl.toFixed(2)}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Order Form */}
              <form onSubmit={handlePlaceOrder} className="order-form">
                {/* Order Side */}
                <div className="form-group">
                  <label>Order Side</label>
                  <div className="btn-group w-100" role="group">
                    <button
                      type="button"
                      className={`btn ${orderSide === 'buy' ? 'btn-success' : 'btn-outline-success'}`}
                      onClick={() => setOrderSide('buy')}
                    >
                      <TrendingUp className="me-1" size={16} />
                      Buy
                    </button>
                    <button
                      type="button"
                      className={`btn ${orderSide === 'sell' ? 'btn-danger' : 'btn-outline-danger'}`}
                      onClick={() => setOrderSide('sell')}
                    >
                      <TrendingDown className="me-1" size={16} />
                      Sell
                    </button>
                  </div>
                </div>

                {/* Order Type */}
                <div className="form-group">
                  <label>Order Type</label>
                  <div className="order-types">
                    {Object.entries(orderTypes).map(([key, type]) => (
                      <div
                        key={key}
                        className={`order-type-card ${orderType === key ? 'selected' : ''}`}
                        onClick={() => setOrderType(key)}
                      >
                        <div className="order-type-header">
                          <span className="order-type-name">{type.name}</span>
                        </div>
                        <small className="order-type-description">{type.description}</small>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Quantity */}
                <div className="form-group">
                  <label>Quantity</label>
                  <input
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    className="form-control"
                    required
                  />
                  {orderSide === 'sell' && currentHolding && (
                    <small className="form-text text-muted">
                      Available to sell: {currentHolding.quantity} shares
                    </small>
                  )}
                </div>

                {/* Dynamic Order Type Fields */}
                {renderOrderTypeFields()}

                {/* Order Summary */}
                {selectedStock && stockQuote && (
                  <div className="order-summary">
                    <h6>Order Summary</h6>
                    <div className="summary-row">
                      <span>Estimated Value:</span>
                      <span className={orderSide === 'buy' ? 'negative' : 'positive'}>
                        ${calculateOrderValue().toFixed(2)}
                      </span>
                    </div>
                    {orderSide === 'buy' && (
                      <div className="summary-row">
                        <span>Available Cash:</span>
                        <span>${availableCash.toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  className={`btn btn-lg w-100 ${orderSide === 'buy' ? 'btn-success' : 'btn-danger'}`}
                  disabled={!selectedStock || loading}
                >
                  {loading ? 'Placing Order...' : `Place ${orderTypes[orderType].name}`}
                </button>
              </form>

              {/* Messages */}
              {error && (
                <div className="alert alert-danger mt-3">
                  {error}
                </div>
              )}

              {success && (
                <div className="alert alert-success mt-3">
                  {success}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Pending Orders Sidebar */}
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h5><Clock className="me-2" size={18} />Pending Orders</h5>
              {selectedStock && (
                <small className="text-muted">for {selectedStock}</small>
              )}
            </div>
            <div className="card-body">
              {pendingOrders.length > 0 ? (
                <div className="pending-orders">
                  {pendingOrders.map((order) => (
                    <div key={order.order_id} className="pending-order">
                      <div className="order-header">
                        <span className={`order-side ${order.side.toLowerCase()}`}>
                          {order.side}
                        </span>
                        <span className="order-type">{order.order_type}</span>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => handleCancelOrder(order.order_id)}
                          title="Cancel Order"
                        >
                          <X size={14} />
                        </button>
                      </div>
                      <div className="order-details">
                        <p><strong>{order.stock_symbol}</strong></p>
                        <p>Qty: {order.quantity}</p>
                        {order.price && <p>Price: ${parseFloat(order.price).toFixed(2)}</p>}
                        {order.stop_price && <p>Stop: ${parseFloat(order.stop_price).toFixed(2)}</p>}
                        {order.limit_price && <p>Limit: ${parseFloat(order.limit_price).toFixed(2)}</p>}
                        <small className="text-muted">
                          {new Date(order.created_at).toLocaleString()}
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted">No pending orders</p>
              )}
            </div>
          </div>

          {/* Cash Balance */}
          <div className="card mt-3">
            <div className="card-body">
              <h6>Available Cash</h6>
              <h4 className="text-success">${availableCash.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</h4>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .trading-container {
          padding: 20px;
        }

        .search-section {
          border-bottom: 1px solid #dee2e6;
          padding-bottom: 1rem;
        }

        .stock-info {
          background-color: #f8f9fa;
          padding: 1rem;
          border-radius: 0.375rem;
          border-left: 4px solid #007bff;
        }

        .current-price {
          font-size: 1.1rem;
          margin: 0;
        }

        .holdings-info p {
          margin: 0.25rem 0;
        }

        .positive {
          color: #28a745;
        }

        .negative {
          color: #dc3545;
        }

        .order-types {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.75rem;
          margin-top: 0.5rem;
        }

        .order-type-card {
          border: 2px solid #dee2e6;
          border-radius: 0.375rem;
          padding: 1rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .order-type-card:hover {
          border-color: #007bff;
          background-color: #f8f9fa;
        }

        .order-type-card.selected {
          border-color: #007bff;
          background-color: #e3f2fd;
        }

        .order-type-header {
          display: flex;
          align-items: center;
          font-weight: 600;
          margin-bottom: 0.25rem;
        }

        .order-type-description {
          color: #6c757d;
          font-size: 0.875rem;
        }

        .order-summary {
          background-color: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 0.375rem;
          padding: 1rem;
          margin-bottom: 1rem;
        }

        .summary-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.5rem;
        }

        .summary-row:last-child {
          margin-bottom: 0;
        }

        .pending-orders {
          max-height: 400px;
          overflow-y: auto;
        }

        .pending-order {
          border: 1px solid #dee2e6;
          border-radius: 0.375rem;
          padding: 0.75rem;
          margin-bottom: 0.75rem;
        }

        .pending-order:last-child {
          margin-bottom: 0;
        }

        .order-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .order-side {
          font-weight: 600;
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.875rem;
        }

        .order-side.buy {
          background-color: #d4edda;
          color: #155724;
        }

        .order-side.sell {
          background-color: #f8d7da;
          color: #721c24;
        }

        .order-type {
          font-size: 0.875rem;
          color: #6c757d;
          font-weight: 500;
        }

        .order-details p {
          margin: 0.25rem 0;
          font-size: 0.9rem;
        }

        @media (max-width: 768px) {
          .order-types {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default EnhancedTrading;
