import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';

const DatabaseTest = () => {
  const [testResults, setTestResults] = useState({
    apiConnection: null,
    portfolio: null,
    cashBalance: null,
    stockQuote: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    runTests();
  }, []);

  const runTests = async () => {
    setLoading(true);
    const results = {
      apiConnection: null,
      portfolio: null,
      cashBalance: null,
      stockQuote: null
    };

    // Test API connection
    try {
      await apiService.testConnection();
      results.apiConnection = { success: true, message: 'API connection successful' };
    } catch (error) {
      results.apiConnection = { success: false, message: error.message };
    }

    // Test portfolio endpoint
    try {
      const portfolio = await apiService.getPortfolio();
      results.portfolio = { 
        success: true, 
        message: `Portfolio loaded: ${portfolio.holdings?.length || 0} holdings` 
      };
    } catch (error) {
      results.portfolio = { success: false, message: error.message };
    }

    // Test cash balance endpoint
    try {
      const balance = await apiService.getBalance();
      results.cashBalance = { 
        success: true, 
        message: `Cash balance: $${balance.cash_balance}` 
      };
    } catch (error) {
      results.cashBalance = { success: false, message: error.message };
    }

    // Test stock quote with database-first approach
    try {
      const quote = await apiService.getStockQuote('AAPL');
      results.stockQuote = { 
        success: true, 
        message: `AAPL quote: $${quote['05. price'] || quote.current_price} (${quote.source || 'API'})` 
      };
    } catch (error) {
      // Try database-only as fallback
      try {
        const cachedQuote = await apiService.getStockQuoteFromDb('AAPL');
        if (cachedQuote && !cachedQuote.error) {
          results.stockQuote = { 
            success: true, 
            message: `AAPL cached quote: $${cachedQuote.current_price} (database only)` 
          };
        } else {
          results.stockQuote = { success: false, message: 'No cached data available' };
        }
      } catch (dbError) {
        results.stockQuote = { success: false, message: error.message };
      }
    }

    setTestResults(results);
    setLoading(false);
  };

  const TestResult = ({ test, result }) => (
    <div style={{ 
      padding: '1rem', 
      margin: '0.5rem 0', 
      borderRadius: '0.5rem',
      backgroundColor: result?.success ? '#d1fae5' : '#fee2e2',
      border: `1px solid ${result?.success ? '#10b981' : '#ef4444'}`
    }}>
      <h4 style={{ margin: '0 0 0.5rem 0', color: result?.success ? '#065f46' : '#991b1b' }}>
        {test}: {result?.success ? '✅ Pass' : '❌ Fail'}
      </h4>
      <p style={{ margin: 0, color: result?.success ? '#065f46' : '#991b1b' }}>
        {result?.message}
      </p>
    </div>
  );

  if (loading) {
    return (
      <div className="card">
        <h2>Testing Database Connection...</h2>
        <div className="loading">Running connectivity tests...</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Database Connection Test</h2>
        <button onClick={runTests} className="btn btn-primary">
          Run Tests Again
        </button>
      </div>
      
      <TestResult test="API Connection" result={testResults.apiConnection} />
      <TestResult test="Portfolio Data" result={testResults.portfolio} />
      <TestResult test="Cash Balance" result={testResults.cashBalance} />
      <TestResult test="Stock Quote" result={testResults.stockQuote} />
      
      <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f3f4f6', borderRadius: '0.5rem' }}>
        <h4>Instructions:</h4>
        <ul>
          <li>Make sure your Flask backend is running on port 5000</li>
          <li>Ensure your MySQL database is running with the correct schema</li>
          <li>Verify your database connection is configured properly</li>
          <li>Check that you have some test data populated in your database</li>
        </ul>
      </div>
    </div>
  );
};

export default DatabaseTest;
