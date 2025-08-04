import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, ComposedChart } from 'recharts';
import apiService from '../services/apiService';

const StockDetail = () => {
  const { symbol } = useParams();
  const [stockData, setStockData] = useState({
    quote: null,
    overview: null,
    dailyData: null,
    intradayData: null,
    news: null
  });
  const [activeTab, setActiveTab] = useState('overview');
  const [chartType, setChartType] = useState('price'); // 'price', 'volume', 'intraday'
  const [chartTimeRange, setChartTimeRange] = useState('30d'); // '1d', '7d', '30d', '90d'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (symbol) {
      fetchStockData(symbol);
    }
  }, [symbol]);

  const fetchStockData = async (stockSymbol) => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch multiple endpoints in parallel with intelligent data fetching
      // Priority: 1. Database-cached data, 2. Fresh API data when needed
      const [quote, overview, dailyData, intradayData, news] = await Promise.allSettled([
        apiService.getStockQuote(stockSymbol), // Backend handles database-first
        apiService.getStockOverview(stockSymbol),
        apiService.getDailyData(stockSymbol),
        apiService.getIntradayData(stockSymbol, '5min'),
        apiService.getNews(stockSymbol)
      ]);

      // Handle quote with fallback to cached data
      let quoteData = null;
      if (quote.status === 'fulfilled') {
        quoteData = quote.value;
      } else {
        // Try to get cached quote data as fallback
        try {
          const cachedQuote = await apiService.getStockQuoteFromDb(stockSymbol);
          if (cachedQuote && !cachedQuote.error) {
            quoteData = cachedQuote;
            console.warn(`Using cached quote data for ${stockSymbol}`);
          }
        } catch (cacheErr) {
          console.warn(`No cached quote data available for ${stockSymbol}`);
        }
      }

      setStockData({
        quote: quoteData,
        overview: overview.status === 'fulfilled' ? overview.value : null,
        dailyData: dailyData.status === 'fulfilled' ? dailyData.value : null,
        intradayData: intradayData.status === 'fulfilled' ? intradayData.value : null,
        news: news.status === 'fulfilled' ? news.value : null
      });
      
    } catch (err) {
      setError(`Failed to fetch data for ${stockSymbol}`);
      console.error('Stock detail error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatLargeNumber = (num) => {
    if (!num) return 'N/A';
    const number = parseFloat(num);
    if (number >= 1e12) return (number / 1e12).toFixed(2) + 'T';
    if (number >= 1e9) return (number / 1e9).toFixed(2) + 'B';
    if (number >= 1e6) return (number / 1e6).toFixed(2) + 'M';
    if (number >= 1e3) return (number / 1e3).toFixed(2) + 'K';
    return number.toFixed(2);
  };

  const prepareDailyChartData = (days = 30) => {
    if (!stockData.dailyData || !stockData.dailyData['Time Series (Daily)']) {
      return [];
    }

    const timeSeries = stockData.dailyData['Time Series (Daily)'];
    return Object.entries(timeSeries)
      .slice(0, days) // Last X days
      .reverse()
      .map(([date, data]) => ({
        date,
        price: parseFloat(data['4. close']),
        volume: parseInt(data['5. volume']),
        high: parseFloat(data['2. high']),
        low: parseFloat(data['3. low']),
        open: parseFloat(data['1. open'])
      }));
  };

  const prepareIntradayChartData = () => {
    if (!stockData.intradayData || !stockData.intradayData['Time Series (5min)']) {
      return [];
    }

    const timeSeries = stockData.intradayData['Time Series (5min)'];
    return Object.entries(timeSeries)
      .slice(0, 78) // Last trading day (6.5 hours * 12 intervals per hour)
      .reverse()
      .map(([timestamp, data]) => ({
        time: timestamp,
        price: parseFloat(data['4. close']),
        volume: parseInt(data['5. volume']),
        high: parseFloat(data['2. high']),
        low: parseFloat(data['3. low']),
        open: parseFloat(data['1. open'])
      }));
  };

  const getChartData = () => {
    if (chartType === 'intraday') {
      return prepareIntradayChartData();
    } else {
      const days = chartTimeRange === '7d' ? 7 : chartTimeRange === '90d' ? 90 : 30;
      return prepareDailyChartData(days);
    }
  };

  // Create fallback chart data from current quote if no historical data available
  const getFallbackChartData = () => {
    if (!quote) return [];
    
    const currentPrice = parseFloat(quote['05. price'] || quote.current_price || 0);
    const change = parseFloat(quote['09. change'] || quote.change_amount || 0);
    const previousPrice = currentPrice - change;
    
    // Create a simple 2-point chart showing previous vs current
    return [
      {
        date: 'Previous',
        price: previousPrice,
        volume: parseInt(quote['06. volume'] || quote.volume || 0) * 0.8
      },
      {
        date: 'Current',
        price: currentPrice,
        volume: parseInt(quote['06. volume'] || quote.volume || 0)
      }
    ];
  };

  if (loading) {
    return <div className="loading">Loading stock data...</div>;
  }

  if (error) {
    return (
      <div>
        <div className="error">{error}</div>
        <Link to="/trading" className="btn btn-primary">
          <ArrowLeft size={16} style={{ marginRight: '0.5rem' }} />
          Back to Trading
        </Link>
      </div>
    );
  }

  const { quote, overview, news } = stockData;
  const chartData = getChartData();
  const fallbackChartData = getFallbackChartData();

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem' }}>
        <Link to="/trading" className="btn btn-secondary" style={{ marginRight: '1rem' }}>
          <ArrowLeft size={16} />
        </Link>
        <div>
          <h1 className="page-title" style={{ margin: 0 }}>
            {symbol}
          </h1>
          {overview && (
            <p style={{ color: '#6b7280', fontSize: '1.1rem', margin: 0 }}>
              {overview.Name}
            </p>
          )}
        </div>
      </div>

      {/* Stock Quote Summary */}
      {quote && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#667eea' }}>
              {formatCurrency(quote['05. price'] || quote.current_price)}
            </div>
            <div className="stat-label">Current Price</div>
          </div>
          
          <div className="stat-card">
            <div className={`stat-value ${parseFloat(quote['09. change'] || quote.change_amount || 0) >= 0 ? 'positive' : 'negative'}`}>
              {parseFloat(quote['09. change'] || quote.change_amount || 0) >= 0 ? '+' : ''}{formatCurrency(quote['09. change'] || quote.change_amount || 0)}
            </div>
            <div className="stat-label">Change</div>
          </div>
          
          <div className="stat-card">
            <div className={`stat-value ${parseFloat(quote['10. change percent']?.replace('%', '') || quote.change_percent?.replace('%', '') || 0) >= 0 ? 'positive' : 'negative'}`}>
              {quote['10. change percent'] || quote.change_percent || 'N/A'}
            </div>
            <div className="stat-label">Change %</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-value">{formatLargeNumber(quote['06. volume'] || quote.volume)}</div>
            <div className="stat-label">Volume</div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <Link to={`/trading?symbol=${symbol}&action=buy`} className="btn btn-success">
          Buy {symbol}
        </Link>
        <Link to={`/trading?symbol=${symbol}&action=sell`} className="btn btn-danger">
          Sell {symbol}
        </Link>
      </div>

      {/* Enhanced Chart Section */}
      {(chartData.length > 0 || quote) && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 className="card-title">
              {chartData.length > 0 ? 'Price Chart' : 'Current Price View'}
            </h3>
            
            {/* Chart Controls - only show when we have historical data */}
            {chartData.length > 0 && (
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                {/* Chart Type Selector */}
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className={`btn ${chartType === 'price' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setChartType('price')}
                    style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
                  >
                    Price
                  </button>
                  <button
                    className={`btn ${chartType === 'volume' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setChartType('volume')}
                    style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
                  >
                    Volume
                  </button>
                  <button
                    className={`btn ${chartType === 'intraday' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setChartType('intraday')}
                    style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
                  >
                    Intraday
                  </button>
                </div>
                
                {/* Time Range Selector (only for daily charts) */}
                {chartType !== 'intraday' && (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className={`btn ${chartTimeRange === '7d' ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => setChartTimeRange('7d')}
                      style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
                    >
                      7D
                    </button>
                    <button
                      className={`btn ${chartTimeRange === '30d' ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => setChartTimeRange('30d')}
                      style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
                    >
                      30D
                    </button>
                    <button
                      className={`btn ${chartTimeRange === '90d' ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => setChartTimeRange('90d')}
                      style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
                    >
                      90D
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              {/* Historical Price Chart */}
              {chartData.length > 0 && chartType === 'price' && (
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#667eea" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey={chartType === 'intraday' ? 'time' : 'date'}
                    tickFormatter={(value) => {
                      if (chartType === 'intraday') {
                        return new Date(value).toLocaleTimeString('en-US', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        });
                      } else {
                        return new Date(value).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric' 
                        });
                      }
                    }}
                  />
                  <YAxis 
                    domain={['dataMin - 5', 'dataMax + 5']}
                    tickFormatter={(value) => `$${value.toFixed(0)}`}
                  />
                  <Tooltip 
                    labelFormatter={(value) => {
                      if (chartType === 'intraday') {
                        return new Date(value).toLocaleString();
                      } else {
                        return new Date(value).toLocaleDateString();
                      }
                    }}
                    formatter={(value, name) => {
                      if (name === 'price') return [formatCurrency(value), 'Price'];
                      return [value, name];
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#667eea" 
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorPrice)"
                  />
                </AreaChart>
              )}

              {/* Fallback Current Price Chart */}
              {chartData.length === 0 && fallbackChartData.length > 0 && (
                <AreaChart data={fallbackChartData}>
                  <defs>
                    <linearGradient id="colorPriceFallback" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#667eea" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date"
                    tickFormatter={(value) => value}
                  />
                  <YAxis 
                    domain={['dataMin - 5', 'dataMax + 5']}
                    tickFormatter={(value) => `$${value.toFixed(0)}`}
                  />
                  <Tooltip 
                    labelFormatter={(value) => value}
                    formatter={(value, name) => {
                      if (name === 'price') return [formatCurrency(value), 'Price'];
                      return [value, name];
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#667eea" 
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorPriceFallback)"
                  />
                </AreaChart>
              )}
              
              {/* Volume Chart */}
              {chartData.length > 0 && chartType === 'volume' && (
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date"
                    tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis 
                    tickFormatter={(value) => {
                      if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B';
                      if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';
                      if (value >= 1e3) return (value / 1e3).toFixed(1) + 'K';
                      return value;
                    }}
                  />
                  <Tooltip 
                    labelFormatter={(date) => new Date(date).toLocaleDateString()}
                    formatter={(value) => [formatLargeNumber(value), 'Volume']}
                  />
                  <Bar 
                    dataKey="volume" 
                    fill="#764ba2"
                    opacity={0.8}
                  />
                </BarChart>
              )}
              
              {/* Intraday Chart */}
              {chartData.length > 0 && chartType === 'intraday' && (
                <ComposedChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="time"
                    tickFormatter={(time) => new Date(time).toLocaleTimeString('en-US', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  />
                  <YAxis 
                    yAxisId="price"
                    orientation="left"
                    domain={['dataMin - 1', 'dataMax + 1']}
                    tickFormatter={(value) => `$${value.toFixed(0)}`}
                  />
                  <YAxis 
                    yAxisId="volume"
                    orientation="right"
                    tickFormatter={(value) => {
                      if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';
                      if (value >= 1e3) return (value / 1e3).toFixed(1) + 'K';
                      return value;
                    }}
                  />
                  <Tooltip 
                    labelFormatter={(time) => new Date(time).toLocaleString()}
                    formatter={(value, name) => {
                      if (name === 'price') return [formatCurrency(value), 'Price'];
                      if (name === 'volume') return [formatLargeNumber(value), 'Volume'];
                      return [value, name];
                    }}
                  />
                  <Line 
                    yAxisId="price"
                    type="monotone" 
                    dataKey="price" 
                    stroke="#667eea" 
                    strokeWidth={2}
                    dot={false}
                  />
                  <Bar 
                    yAxisId="volume"
                    dataKey="volume" 
                    fill="#764ba2"
                    opacity={0.3}
                  />
                </ComposedChart>
              )}
            </ResponsiveContainer>
          </div>
          
          {/* Chart Info */}
          <div style={{ 
            marginTop: '1rem', 
            padding: '1rem', 
            backgroundColor: '#f8fafc', 
            borderRadius: '0.5rem',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
            gap: '1rem',
            fontSize: '0.9rem'
          }}>
            {chartData.length > 0 ? (
              <>
                <div>
                  <div style={{ color: '#6b7280' }}>High</div>
                  <div style={{ fontWeight: 'bold' }}>
                    {formatCurrency(Math.max(...chartData.map(d => d.high || d.price)))}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280' }}>Low</div>
                  <div style={{ fontWeight: 'bold' }}>
                    {formatCurrency(Math.min(...chartData.map(d => d.low || d.price)))}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280' }}>Avg Volume</div>
                  <div style={{ fontWeight: 'bold' }}>
                    {formatLargeNumber(chartData.reduce((sum, d) => sum + (d.volume || 0), 0) / chartData.length)}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280' }}>Data Points</div>
                  <div style={{ fontWeight: 'bold' }}>{chartData.length}</div>
                </div>
              </>
            ) : quote ? (
              <>
                <div>
                  <div style={{ color: '#6b7280' }}>Current Price</div>
                  <div style={{ fontWeight: 'bold' }}>
                    {formatCurrency(quote['05. price'] || quote.current_price)}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280' }}>Daily Change</div>
                  <div style={{ fontWeight: 'bold' }}>
                    {formatCurrency(quote['09. change'] || quote.change_amount || 0)}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280' }}>Volume</div>
                  <div style={{ fontWeight: 'bold' }}>
                    {formatLargeNumber(quote['06. volume'] || quote.volume)}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280' }}>Data Source</div>
                  <div style={{ fontWeight: 'bold' }}>Real-time Quote</div>
                </div>
              </>
            ) : null}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', borderBottom: '1px solid #e5e7eb' }}>
          <button
            className={`btn ${activeTab === 'overview' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={`btn ${activeTab === 'financials' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('financials')}
          >
            Financials
          </button>
          <button
            className={`btn ${activeTab === 'news' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('news')}
          >
            News
          </button>
        </div>

        {activeTab === 'overview' && overview && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
              <div>
                <h4>Company Information</h4>
                <table className="table">
                  <tbody>
                    <tr><td><strong>Sector</strong></td><td>{overview.Sector || 'N/A'}</td></tr>
                    <tr><td><strong>Industry</strong></td><td>{overview.Industry || 'N/A'}</td></tr>
                    <tr><td><strong>Market Cap</strong></td><td>{formatLargeNumber(overview.MarketCapitalization)}</td></tr>
                    <tr><td><strong>Employees</strong></td><td>{formatLargeNumber(overview.FullTimeEmployees)}</td></tr>
                    <tr><td><strong>Exchange</strong></td><td>{overview.Exchange || 'N/A'}</td></tr>
                  </tbody>
                </table>
              </div>
              
              <div>
                <h4>Key Metrics</h4>
                <table className="table">
                  <tbody>
                    <tr><td><strong>P/E Ratio</strong></td><td>{overview.PERatio || 'N/A'}</td></tr>
                    <tr><td><strong>EPS</strong></td><td>{formatCurrency(overview.EPS)}</td></tr>
                    <tr><td><strong>Beta</strong></td><td>{overview.Beta || 'N/A'}</td></tr>
                    <tr><td><strong>52W High</strong></td><td>{formatCurrency(overview['52WeekHigh'])}</td></tr>
                    <tr><td><strong>52W Low</strong></td><td>{formatCurrency(overview['52WeekLow'])}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            {overview.Description && (
              <div style={{ marginTop: '2rem' }}>
                <h4>About</h4>
                <p style={{ lineHeight: '1.8', color: '#374151' }}>{overview.Description}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'financials' && overview && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
              <div>
                <h4>Revenue & Profitability</h4>
                <table className="table">
                  <tbody>
                    <tr><td><strong>Revenue (TTM)</strong></td><td>{formatLargeNumber(overview.RevenueTTM)}</td></tr>
                    <tr><td><strong>Gross Profit (TTM)</strong></td><td>{formatLargeNumber(overview.GrossProfitTTM)}</td></tr>
                    <tr><td><strong>EBITDA</strong></td><td>{formatLargeNumber(overview.EBITDA)}</td></tr>
                    <tr><td><strong>Net Income (TTM)</strong></td><td>{formatLargeNumber(overview.NetIncomeTTM)}</td></tr>
                    <tr><td><strong>Profit Margin</strong></td><td>{overview.ProfitMargin ? (parseFloat(overview.ProfitMargin) * 100).toFixed(2) + '%' : 'N/A'}</td></tr>
                  </tbody>
                </table>
              </div>
              
              <div>
                <h4>Valuation</h4>
                <table className="table">
                  <tbody>
                    <tr><td><strong>Book Value</strong></td><td>{formatCurrency(overview.BookValue)}</td></tr>
                    <tr><td><strong>P/B Ratio</strong></td><td>{overview.PriceToBookRatio || 'N/A'}</td></tr>
                    <tr><td><strong>P/S Ratio</strong></td><td>{overview.PriceToSalesRatioTTM || 'N/A'}</td></tr>
                    <tr><td><strong>PEG Ratio</strong></td><td>{overview.PEGRatio || 'N/A'}</td></tr>
                    <tr><td><strong>Dividend Yield</strong></td><td>{overview.DividendYield ? (parseFloat(overview.DividendYield) * 100).toFixed(2) + '%' : 'N/A'}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'news' && (
          <div>
            {news && news.feed && news.feed.length > 0 ? (
              <div style={{ display: 'grid', gap: '1.5rem' }}>
                {news.feed.slice(0, 10).map((article, index) => (
                  <div key={index} style={{ 
                    padding: '1.5rem', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '0.5rem',
                    backgroundColor: '#fafafa'
                  }}>
                    <h4 style={{ marginBottom: '0.5rem' }}>
                      <a 
                        href={article.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ color: '#667eea', textDecoration: 'none' }}
                      >
                        {article.title}
                      </a>
                    </h4>
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
                No news available for this stock.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StockDetail;
