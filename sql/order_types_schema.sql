-- Enhanced database schema for order types
USE portfolio_manager;

-- Create orders table to track pending orders
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(50) DEFAULT 'default_user',
    stock_symbol VARCHAR(50) NOT NULL,
    order_type ENUM('MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT') NOT NULL,
    side ENUM('BUY', 'SELL') NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    price DECIMAL(10, 2) NULL, -- For limit orders
    stop_price DECIMAL(10, 2) NULL, -- For stop and stop-limit orders
    limit_price DECIMAL(10, 2) NULL, -- For stop-limit orders
    status ENUM('PENDING', 'FILLED', 'CANCELLED', 'EXPIRED') DEFAULT 'PENDING',
    time_in_force ENUM('DAY', 'GTC') DEFAULT 'DAY', -- Good Till Cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filled_at TIMESTAMP NULL,
    filled_price DECIMAL(10, 2) NULL,
    filled_quantity DECIMAL(10, 2) NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (stock_symbol),
    INDEX idx_status (status),
    INDEX idx_user (user_id),
    INDEX idx_type (order_type),
    INDEX idx_created (created_at)
);

-- Update trades table to include order_id reference
ALTER TABLE trades ADD COLUMN order_id INT NULL;
ALTER TABLE trades ADD COLUMN order_type ENUM('MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT') DEFAULT 'MARKET';

-- Add foreign key constraint (optional)
-- ALTER TABLE trades ADD FOREIGN KEY (order_id) REFERENCES orders(order_id);

-- Create index for better performance
CREATE INDEX idx_trades_order_id ON trades(order_id);
