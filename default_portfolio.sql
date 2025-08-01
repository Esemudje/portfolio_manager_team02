CREATE DATABASE IF NOT EXISTS portfolio;
USE portfolio;

-- Create available_stock table with api information
CREATE TABLE api_stock_information(
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_symbol VARCHAR(50) NOT NULL,
    open_price DOUBLE NOT NULL,
    high_price DOUBLE NOT NULL,
    low_price DOUBLE NOT NULL,
    current_price DOUBLE NOT NULL,
    volume DOUBLE NOT NULL,
    latest_trading_day DATETIME NOT NULL,
    previous_close DOUBLE NOT NULL,
    change_amount DOUBLE NOT NULL,
    change_percent DOUBLE NOT NULL
);


-- Create trades table
CREATE TABLE trades (
    trade_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_symbol VARCHAR(50) NOT NULL,
    trade_type ENUM('BUY', 'SELL') NOT NULL,
    price_at_trade DOUBLE NOT NULL,
    quantity DOUBLE NOT NULL,
    trade_date DATETIME NOT NULL
);

-- Create holdings table
CREATE TABLE holdings (
    holding_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_symbol VARCHAR(50) NOT NULL,
    quantity DOUBLE NOT NULL,
    average_cost DOUBLE NOT NULL
);

-- Create profit_and_loss table
CREATE TABLE profit_and_loss (
    pl_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    trade_id INT NOT NULL,
    stock_symbol VARCHAR(50) NOT NULL,
    realized_p_l DOUBLE NOT NULL,
    unrealized_p_l DOUBLE,
    FOREIGN KEY (stock_id) REFERENCES api_stock_information(stock_id),
    FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);







