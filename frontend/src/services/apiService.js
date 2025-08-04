import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api', // This will use the proxy configured in package.json
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response.data;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    // Handle different types of errors
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout - please try again');
    }
    
    if (!error.response) {
      throw new Error('Network error - please check your connection');
    }
    
    const { status, data } = error.response;
    
    switch (status) {
      case 404:
        throw new Error(data?.error || 'Stock symbol not found');
      case 429:
        throw new Error('Rate limit exceeded - please wait a moment');
      case 500:
        throw new Error(data?.error || 'Server error - please try again later');
      default:
        throw new Error(data?.error || `Request failed with status ${status}`);
    }
  }
);

const apiService = {
  // Test API connection
  testConnection: async () => {
    return api.get('/test-connection');
  },

  // Database-first stock quote (uses cached data when available)
  getStockQuote: async (symbol) => {
    // Backend automatically checks database first, then API if needed
    return api.get(`/stocks/${symbol}`);
  },

  // Get stock quote from database only (no API fallback)
  getStockQuoteFromDb: async (symbol) => {
    return api.get(`/stocks/${symbol}/db-only`);
  },

  // Get company overview
  getStockOverview: async (symbol) => {
    return api.get(`/stocks/${symbol}/overview`);
  },

  // Get intraday data
  getIntradayData: async (symbol, interval = '5min') => {
    return api.get(`/stocks/${symbol}/intraday`, {
      params: { interval }
    });
  },

  // Get daily data
  getDailyData: async (symbol) => {
    return api.get(`/stocks/${symbol}/daily`);
  },

  // Get news and sentiment
  getNews: async (symbol, topics = null) => {
    const params = topics ? { topics } : {};
    return api.get(`/stocks/${symbol}/news`, { params });
  },

  // Get earnings data
  getEarnings: async (symbol) => {
    return api.get(`/stocks/${symbol}/earnings`);
  },

  // Portfolio Management Functions - Connected to MySQL Database
  
  // Get complete portfolio summary with holdings and P&L
  getPortfolio: async (symbol = null) => {
    const params = symbol ? { symbol } : {};
    return api.get('/portfolio', { params });
  },

  // Get trade history
  getTrades: async (symbol = null, limit = 50) => {
    const params = { limit };
    if (symbol) params.symbol = symbol;
    return api.get('/portfolio/trades', { params });
  },

  // Get current cash balance
  getBalance: async (userId = 'default_user') => {
    return api.get('/portfolio/cash', { 
      params: { user_id: userId } 
    });
  },

  // Get portfolio performance metrics
  getPerformance: async (days = 30) => {
    return api.get('/portfolio/performance', { 
      params: { days } 
    });
  },

  // Trading Functions - Execute real trades
  
  // Execute buy order
  buyStock: async (symbol, quantity, cash = null, userId = 'default_user') => {
    return api.post('/trade/buy', {
      symbol: symbol.toUpperCase(),
      quantity: parseInt(quantity),
      cash,
      user_id: userId
    });
  },

  // Execute sell order
  sellStock: async (symbol, quantity, userId = 'default_user') => {
    return api.post('/trade/sell', {
      symbol: symbol.toUpperCase(),
      quantity: parseInt(quantity),
      user_id: userId
    });
  },

  // Get FIFO holdings information for a symbol
  getHoldingsInfo: async (symbol) => {
    return api.get(`/trade/holdings/${symbol.toUpperCase()}`);
  }
};

export default apiService;
