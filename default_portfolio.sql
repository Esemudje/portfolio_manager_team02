CREATE DATABASE IF NOT EXISTS portfolio;
USE portfolio;

-- Create available_stock table
CREATE TABLE available_stock (
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_symbol VARCHAR(50) NOT NULL,
    stock_name VARCHAR(50) NOT NULL,
    current_price DOUBLE NOT NULL,
    INDEX idx_stock_symbol (stock_symbol)
);


-- Create trades table
CREATE TABLE trades (
    trade_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    stock_symbol VARCHAR(50) NOT NULL,
    trade_type ENUM('BUY', 'SELL') NOT NULL,
    price_at_trade DOUBLE NOT NULL,
    quantity DOUBLE NOT NULL,
    trade_date DATETIME NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES available_stock(stock_id)
);

-- Create holdings table
CREATE TABLE holdings (
    holding_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    stock_symbol VARCHAR(50) NOT NULL,
    quantity DOUBLE NOT NULL,
    average_cost DOUBLE NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES available_stock(stock_id)
);

-- Create profit_and_loss table
CREATE TABLE profit_and_loss (
    pl_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    trade_id INT NOT NULL,
    stock_symbol VARCHAR(50) NOT NULL,
    realized_p_l DOUBLE NOT NULL,
    unrealized_p_l DOUBLE,
    FOREIGN KEY (stock_id) REFERENCES available_stock(stock_id),
    FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);

-- fill tables with dummy values

INSERT INTO available_stock (stock_symbol, stock_name, current_price)
VALUES 
    ('AAPL', 'Apple', 195.60),
    ('GOOGL', 'Alphabet Inc.', 2742.50),
    ('AMZN', 'Amazon', 236.50);

-- Insert trades (buy/sell operations for each stock)
INSERT INTO trades (stock_id, stock_symbol, trade_type, price_at_trade, quantity, trade_date)
VALUES 
    (1, 'AAPL', 'BUY', 190.00, 10, NOW()),
    (1, 'AAPL', 'BUY', 200.00, 5, NOW()),
    (2, 'GOOGL', 'BUY', 2700.00, 2, NOW()),
    (2, 'GOOGL', 'SELL', 2750.00, 1, NOW()),
    (3, 'AMZN', 'BUY', 230.00, 3, NOW());


-- Reflect the current holdings after the trades
INSERT INTO holdings (stock_id, stock_symbol, quantity, average_cost)
VALUES 
    (1, 'AAPL', 15, 193.33),       -- 10 at 190 + 5 at 200 = weighted avg 193.33
    (2, 'GOOGL', 1, 2700.00),      -- Bought 2, sold 1 → 1 remaining
    (3, 'AMZN', 3, 230.00);        -- No sell yet, avg cost = 230


-- Realized and unrealized profit and loss
INSERT INTO profit_and_loss (stock_id, trade_id, stock_symbol, realized_p_l, unrealized_p_l)
VALUES 
    (2, 4, 'GOOGL', 50.00, NULL),         -- Sold one GOOGL at 2750, bought at 2700 → +50 realized
    (1, 2, 'AAPL', 0.00, 36.00),          -- No sell yet, unrealized gain: (current 195.60 - avg 193.33) * 15
    (3, 5, 'AMZN', 0.00, 19.50);          -- (236.50 - 230.00) * 3 = 19.50 unrealized gain




