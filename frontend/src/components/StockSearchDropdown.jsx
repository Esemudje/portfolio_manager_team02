import React, { useState, useEffect, useRef } from 'react';
import { Search, TrendingUp, DollarSign, Building2 } from 'lucide-react';
import apiService from '../services/apiService';

const StockSearchDropdown = ({ onStockSelect, className = '' }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchInputRef = useRef(null);
  const resultsRef = useRef(null);

  // Debounce search to avoid too many API calls
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      if (searchTerm.trim().length >= 2) {
        performSearch(searchTerm.trim());
      } else {
        setSearchResults([]);
        setShowResults(false);
      }
    }, 300);

    return () => clearTimeout(delayedSearch);
  }, [searchTerm]);

  const performSearch = async (query) => {
    setIsSearching(true);
    try {
      const response = await apiService.searchStocks(query, 15);
      setSearchResults(response.results || []);
      setShowResults(true);
      setSelectedIndex(-1);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
      setShowResults(false);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyDown = (e) => {
    if (!showResults || searchResults.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < searchResults.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < searchResults.length) {
          selectStock(searchResults[selectedIndex]);
        } else if (searchResults.length > 0) {
          selectStock(searchResults[0]);
        }
        break;
      case 'Escape':
        setShowResults(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const selectStock = (stock) => {
    setSearchTerm(stock.symbol);
    setShowResults(false);
    setSelectedIndex(-1);
    onStockSelect(stock.symbol, stock);
  };

  const handleInputClick = () => {
    if (searchResults.length > 0) {
      setShowResults(true);
    }
  };

  const handleBlur = (e) => {
    // Delay hiding results to allow clicking on them
    setTimeout(() => {
      if (!resultsRef.current?.contains(document.activeElement)) {
        setShowResults(false);
        setSelectedIndex(-1);
      }
    }, 150);
  };

  return (
    <div className={`stock-search-container ${className}`}>
      <div className="search-input-container">
        <Search className="search-icon" size={20} />
        <input
          ref={searchInputRef}
          type="text"
          className="search-input"
          placeholder="Search by company name or symbol..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleKeyDown}
          onClick={handleInputClick}
          onBlur={handleBlur}
          autoComplete="off"
        />
        {isSearching && (
          <div className="search-spinner">
            <div className="spinner"></div>
          </div>
        )}
      </div>

      {showResults && searchResults.length > 0 && (
        <div ref={resultsRef} className="search-results-dropdown">
          {searchResults.map((stock, index) => (
            <div
              key={stock.symbol}
              className={`search-result-item ${index === selectedIndex ? 'selected' : ''}`}
              onClick={() => selectStock(stock)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div className="result-main">
                <div className="result-header">
                  <span className="result-symbol">{stock.symbol}</span>
                  <span className="result-emoji">{stock.sector_emoji}</span>
                </div>
                <div className="result-name">{stock.name}</div>
              </div>
              <div className="result-meta">
                <div className="result-sector">
                  <Building2 size={14} />
                  {stock.sector}
                </div>
                <div className="result-marketcap">
                  <DollarSign size={14} />
                  {stock.market_cap_formatted}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showResults && searchResults.length === 0 && !isSearching && searchTerm.length >= 2 && (
        <div ref={resultsRef} className="search-results-dropdown">
          <div className="no-results">
            No stocks found for "{searchTerm}"
          </div>
        </div>
      )}

      <style jsx>{`
        .stock-search-container {
          position: relative;
          width: 100%;
        }

        .search-input-container {
          position: relative;
          display: flex;
          align-items: center;
        }

        .search-input {
          width: 100%;
          padding: 12px 16px 12px 40px;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 16px;
          transition: all 0.2s ease;
          background: white;
        }

        .search-input:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .search-icon {
          position: absolute;
          left: 12px;
          color: #6b7280;
          z-index: 1;
        }

        .search-spinner {
          position: absolute;
          right: 12px;
          display: flex;
          align-items: center;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #e5e7eb;
          border-top: 2px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .search-results-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
          max-height: 400px;
          overflow-y: auto;
          z-index: 1000;
          margin-top: 4px;
        }

        .search-result-item {
          padding: 12px 16px;
          cursor: pointer;
          border-bottom: 1px solid #f3f4f6;
          transition: background-color 0.2s ease;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .search-result-item:hover,
        .search-result-item.selected {
          background-color: #f8fafc;
        }

        .search-result-item:last-child {
          border-bottom: none;
        }

        .result-main {
          flex: 1;
        }

        .result-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 4px;
        }

        .result-symbol {
          font-weight: 600;
          color: #1f2937;
          font-size: 14px;
        }

        .result-emoji {
          font-size: 16px;
        }

        .result-name {
          font-size: 13px;
          color: #6b7280;
          line-height: 1.3;
          margin-bottom: 4px;
        }

        .result-meta {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 2px;
          font-size: 12px;
          color: #6b7280;
          min-width: 120px;
        }

        .result-sector,
        .result-marketcap {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .no-results {
          padding: 16px;
          text-align: center;
          color: #6b7280;
          font-style: italic;
        }

        @media (max-width: 768px) {
          .result-meta {
            display: none;
          }
          
          .search-result-item {
            padding: 16px;
          }
        }
      `}</style>
    </div>
  );
};

export default StockSearchDropdown;
