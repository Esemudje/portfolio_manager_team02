import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, Calendar, DollarSign } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import apiService from '../services/apiService';

const StockDetail = () => {
  const { symbol } = useParams();
  const [stockData, setStockData] = useState({
    quote: null,
    overview: null,
    dailyData: null,
    news: null
  });
  const [activeTab, setActiveTab] = useState('overview');
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
      
      // Fetch multiple endpoints in parallel
      const [quote, overview, dailyData, news] = await Promise.allSettled([
        apiService.getStockQuote(stockSymbol),
        apiService.getStockOverview(stockSymbol),
        apiService.getDailyData(stockSymbol),
        apiService.getNews(stockSymbol)
      ]);

      setStockData({
        quote: quote.status === 'fulfilled' ? quote.value : null,
        overview: overview.status === 'fulfilled' ? overview.value : null,
        dailyData: dailyData.status === 'fulfilled' ? dailyData.value : null,
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

  const prepareChartData = () => {
    if (!stockData.dailyData || !stockData.dailyData['Time Series (Daily)']) {
      return [];
    }

    const timeSeries = stockData.dailyData['Time Series (Daily)'];
    return Object.entries(timeSeries)
      .slice(0, 30) // Last 30 days
      .reverse()
      .map(([date, data]) => ({
        date,
        price: parseFloat(data['4. close']),
        volume: parseInt(data['5. volume'])
      }));
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
  const chartData = prepareChartData();

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
              {formatCurrency(quote['05. price'])}
            </div>
            <div className="stat-label">Current Price</div>
          </div>
          
          <div className="stat-card">
            <div className={`stat-value ${parseFloat(quote['09. change'] || 0) >= 0 ? 'positive' : 'negative'}`}>
              {parseFloat(quote['09. change'] || 0) >= 0 ? '+' : ''}{formatCurrency(quote['09. change'])}
            </div>
            <div className="stat-label">Change</div>
          </div>
          
          <div className="stat-card">
            <div className={`stat-value ${parseFloat(quote['10. change percent']?.replace('%', '') || 0) >= 0 ? 'positive' : 'negative'}`}>
              {quote['10. change percent'] || 'N/A'}
            </div>
            <div className="stat-label">Change %</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-value">{formatLargeNumber(quote['06. volume'])}</div>
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

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 className="card-title">Price Chart (30 Days)</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis 
                  domain={['dataMin - 5', 'dataMax + 5']}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip 
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
                  formatter={(value) => [formatCurrency(value), 'Price']}
                />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#667eea" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
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
