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

  // Get real-time stock quote
  getStockQuote: async (symbol) => {
    return api.get(`/stocks/${symbol}`);
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

  // Portfolio and trading functions (these would connect to your backend database)
  // For now, these are placeholder functions that would need to be implemented
  
  getPortfolio: async () => {
    // This would get portfolio data from your MySQL database
    // return api.get('/portfolio');
    throw new Error('Portfolio API not yet implemented');
  },

  getHoldings: async () => {
    // This would get current holdings from your MySQL database
    // return api.get('/holdings');
    throw new Error('Holdings API not yet implemented');
  },

  getTrades: async () => {
    // This would get trade history from your MySQL database
    // return api.get('/trades');
    throw new Error('Trades API not yet implemented');
  },

  executeTrade: async (tradeData) => {
    // This would execute a trade and update your MySQL database
    // return api.post('/trades', tradeData);
    throw new Error('Trade execution API not yet implemented');
  },

  getBalance: async () => {
    // This would get current cash balance from your MySQL database
    // return api.get('/balance');
    throw new Error('Balance API not yet implemented');
  }
};

export default apiService;
