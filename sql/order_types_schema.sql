-- Enhanced database schema for order types
USE portfolio_manager;

-- Create orders table to track pending orders
-- Add new table: orders for managing order types
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    stock_symbol VARCHAR(10) NOT NULL,
    order_type ENUM('MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT') NOT NULL,
    side ENUM('BUY', 'SELL') NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    price DECIMAL(10, 2),
    stop_price DECIMAL(10, 2),
    limit_price DECIMAL(10, 2),
    status ENUM('PENDING', 'FILLED', 'CANCELLED', 'PARTIALLY_FILLED', 'EXPIRED') NOT NULL DEFAULT 'PENDING',
    time_in_force ENUM('DAY', 'GTC') DEFAULT 'DAY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    filled_at TIMESTAMP NULL,
    filled_price DECIMAL(10, 2),
    filled_quantity DECIMAL(10, 2),

    -- Performance indexes
    INDEX idx_user (user_id),
    INDEX idx_symbol (stock_symbol),
    INDEX idx_status (status),
    INDEX idx_type (order_type),
    INDEX idx_side (side),
    INDEX idx_created (created_at),
    INDEX idx_filled (filled_at),
    
    -- Composite indexes for common query patterns
    INDEX idx_user_status (user_id, status),
    INDEX idx_symbol_status (stock_symbol, status),
    INDEX idx_user_symbol (user_id, stock_symbol),
    INDEX idx_status_created (status, created_at),
    INDEX idx_type_status (order_type, status),
    INDEX idx_user_symbol_status (user_id, stock_symbol, status)
);

-- Note: trades table already includes order_id and order_type in default_portfolio.sql
-- and has appropriate indexes. No further ALTERs needed here to avoid duplication.
