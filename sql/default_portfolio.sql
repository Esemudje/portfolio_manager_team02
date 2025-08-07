CREATE DATABASE IF NOT EXISTS portfolio_manager;
USE portfolio_manager;

-- Stock information table (from API data)
CREATE TABLE IF NOT EXISTS api_stock_information(
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_symbol VARCHAR(50) NOT NULL UNIQUE,
    open_price DECIMAL(10, 2) NOT NULL,
    high_price DECIMAL(10, 2) NOT NULL,
    low_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    latest_trading_day DATETIME NOT NULL,
    previous_close DECIMAL(10, 2) NOT NULL,
    change_amount DECIMAL(10, 2) NOT NULL,
    change_percent DECIMAL(10, 4) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (stock_symbol)
);

-- Holdings table to track current positions
CREATE TABLE IF NOT EXISTS holdings (
    holding_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_symbol VARCHAR(50) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    average_cost DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (stock_symbol),
    UNIQUE KEY unique_holding (stock_symbol)
);

-- Trades table to track all buy/sell transactions
CREATE TABLE IF NOT EXISTS trades (
    trade_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_symbol VARCHAR(50) NOT NULL,
    trade_type ENUM('BUY', 'SELL') NOT NULL,
    price_at_trade DECIMAL(10, 2) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    trade_date DATETIME NOT NULL,
    realized_pnl DECIMAL(10, 2) DEFAULT NULL, -- Only for SELL trades
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (stock_symbol),
    INDEX idx_date (trade_date),
    INDEX idx_type (trade_type)
);

-- User cash balance table
CREATE TABLE IF NOT EXISTS user_balance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) DEFAULT 'default_user',
    cash_balance DECIMAL(15, 2) DEFAULT 5000000.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user (user_id)
);

-- Insert default cash balance
INSERT IGNORE INTO user_balance (user_id, cash_balance) VALUES ('default_user', 5000000.00);

-- Profit and Loss tracking table (optional - for detailed P&L history)
CREATE TABLE IF NOT EXISTS profit_and_loss (
    pl_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_symbol VARCHAR(50) NOT NULL,
    trade_id INT NOT NULL,
    realized_pnl DECIMAL(10, 2),
    unrealized_pnl DECIMAL(10, 2),
    calculation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trade_id) REFERENCES trades(trade_id),
    INDEX idx_symbol (stock_symbol),
    INDEX idx_date (calculation_date)
);

CREATE TABLE IF NOT EXISTS news (
	headline_id INT PRIMARY KEY AUTO_INCREMENT,
    headline TEXT NOT NULL,
    reported_by TEXT NOT NULL
);

-- NASDAQ Companies table for search functionality
CREATE TABLE IF NOT EXISTS nasdaq_companies (
  Symbol VARCHAR(10) NOT NULL,
  Name   VARCHAR(255) NOT NULL,
  Sector VARCHAR(128),
  MarketCap BIGINT,
  PRIMARY KEY (Symbol),
  INDEX idx_name (Name),
  INDEX idx_sector (Sector),
  INDEX idx_marketcap (MarketCap)
);

-- Only run insert statement once, comment out when done to prevent duplicates
INSERT INTO news (headline, reported_by) VALUES
("S&P 500 falls after weak economic data and more tariff threats. The S&P 500
 pulled back Tuesday as traders digested weaker-than-expected economic data and new tariff comments from President Donald Trump, stoking concerns about the state of the U.S. economy", "CNBC"),
 ("Trump says pharma tariffs could eventually reach 250%", "Yahoo Finance"),
 ("Trade school stocks soar as demand for skilled labor rises", "Bloomberg"),
 ("Eyes on gravity SUV ramp, path to profitability for Lucid earnings", "Yahoo Finance"),
 ("Starbucks under pressure again as Brazilian tariffs hike coffee costs", "Yahoo Finance"),
 ("Record surge in past-due student loans adds to US debt burden", "Bloomberg"),
 ("Gold Gains as Weaker Economic Data Boosts Fed Rate Cut Bets", "Bloomberg"),
("From ingredient costs to sagging demand, tariffs further pinch company earnings", "Reuters"),
("Stock market today: Dow, S&P 500, Nasdaq mixed as Wall Street eyes earnings, trade tensions", "Yahoo Finance"),
("Palantir stock pops, Pfizer beats, Caterpillar warns of tariff impact", "Yahoo Finance");









