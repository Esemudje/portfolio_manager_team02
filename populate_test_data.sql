-- =====================================================
-- Portfolio Manager Test Data Population Script
-- =====================================================
-- This script populates the database with test stock data
-- for major companies to enable trading functionality testing.
-- 
-- Usage:
-- 1. Ensure the database and tables are created (run default_portfolio.sql first)
-- 2. Run this script: mysql -u username -p portfolio_manager < populate_test_data.sql
-- 3. Or execute in MySQL Workbench
-- =====================================================

USE portfolio_manager;

-- Clear existing test data (optional - remove if you want to keep existing data)
-- DELETE FROM api_stock_information;
-- DELETE FROM user_balance WHERE user_id != 'default_user';

-- =====================================================
-- POPULATE STOCK INFORMATION TABLE
-- =====================================================
-- Insert or update stock data for major companies
INSERT INTO api_stock_information (
    stock_symbol, open_price, high_price, low_price, current_price,
    volume, latest_trading_day, previous_close, change_amount, change_percent
) VALUES 
    -- Tech Giants
    ('AAPL', 209.05, 209.50, 207.10, 207.57, 45000000, '2025-08-01', 209.05, -1.48, -0.71),
    ('MSFT', 420.00, 421.00, 417.50, 418.50, 25000000, '2025-08-01', 419.20, -0.70, -0.17),
    ('GOOGL', 2755.00, 2760.00, 2745.00, 2750.00, 1200000, '2025-08-01', 2752.30, -2.30, -0.08),
    ('AMZN', 3185.00, 3190.00, 3175.00, 3180.00, 8000000, '2025-08-01', 3182.50, -2.50, -0.08),
    ('META', 497.00, 498.50, 494.00, 495.75, 18000000, '2025-08-01', 496.20, -0.45, -0.09),
    
    -- AI & Semiconductor
    ('NVDA', 878.00, 880.00, 872.00, 875.25, 35000000, '2025-08-01', 876.75, -1.50, -0.17),
    ('AMD', 155.20, 157.00, 154.50, 156.80, 25000000, '2025-08-01', 155.90, 0.90, 0.58),
    ('INTC', 34.20, 34.80, 33.90, 34.50, 40000000, '2025-08-01', 34.10, 0.40, 1.17),
    
    -- Electric Vehicles & Energy
    ('TSLA', 250.00, 252.00, 247.00, 248.50, 45000000, '2025-08-01', 250.00, -1.50, -0.60),
    ('RIVN', 18.50, 19.20, 18.10, 18.75, 15000000, '2025-08-01', 18.60, 0.15, 0.81),
    
    -- Financial Services
    ('JPM', 216.50, 217.00, 215.20, 215.80, 12000000, '2025-08-01', 216.30, -0.50, -0.23),
    ('BAC', 42.80, 43.20, 42.50, 42.90, 35000000, '2025-08-01', 42.75, 0.15, 0.35),
    ('WFC', 58.90, 59.50, 58.40, 59.20, 18000000, '2025-08-01', 58.80, 0.40, 0.68),
    ('GS', 485.00, 488.00, 482.00, 486.50, 2500000, '2025-08-01', 484.20, 2.30, 0.47),
    
    -- Payment Networks
    ('V', 286.00, 287.00, 284.50, 285.40, 5500000, '2025-08-01', 285.90, -0.50, -0.17),
    ('MA', 478.50, 480.00, 476.80, 479.20, 3200000, '2025-08-01', 478.90, 0.30, 0.06),
    
    -- Healthcare & Pharma
    ('JNJ', 165.80, 166.50, 165.20, 166.10, 8500000, '2025-08-01', 165.70, 0.40, 0.24),
    ('PFE', 28.90, 29.40, 28.70, 29.15, 45000000, '2025-08-01', 28.85, 0.30, 1.04),
    ('UNH', 525.00, 528.00, 522.50, 526.80, 3800000, '2025-08-01', 524.20, 2.60, 0.50),
    ('ABBV', 176.50, 177.80, 175.90, 177.20, 7200000, '2025-08-01', 176.80, 0.40, 0.23),
    
    -- Consumer & Retail
    ('AMZN', 3185.00, 3190.00, 3175.00, 3180.00, 8000000, '2025-08-01', 3182.50, -2.50, -0.08),
    ('WMT', 168.90, 169.80, 168.20, 169.45, 12000000, '2025-08-01', 168.75, 0.70, 0.41),
    ('HD', 385.20, 387.50, 383.80, 386.90, 4500000, '2025-08-01', 385.60, 1.30, 0.34),
    ('NKE', 82.40, 83.20, 81.90, 82.85, 8500000, '2025-08-01', 82.50, 0.35, 0.42),
    
    -- Energy
    ('XOM', 117.80, 118.90, 117.20, 118.40, 18000000, '2025-08-01', 117.90, 0.50, 0.42),
    ('CVX', 162.30, 163.80, 161.70, 163.25, 8200000, '2025-08-01', 162.45, 0.80, 0.49),
    
    -- Aerospace & Defense
    ('BA', 178.90, 180.50, 177.80, 179.65, 6800000, '2025-08-01', 178.95, 0.70, 0.39),
    ('LMT', 445.20, 448.00, 443.50, 446.80, 1200000, '2025-08-01', 445.60, 1.20, 0.27),
    
    -- Media & Entertainment
    ('DIS', 98.50, 99.20, 97.80, 98.90, 15000000, '2025-08-01', 98.45, 0.45, 0.46),
    ('NFLX', 425.80, 428.50, 423.90, 427.20, 4200000, '2025-08-01', 425.95, 1.25, 0.29),
    
    -- Berkshire Hathaway (popular investment stock)
    ('BRK.B', 435.20, 437.80, 434.50, 436.90, 3500000, '2025-08-01', 435.85, 1.05, 0.24)

ON DUPLICATE KEY UPDATE
    open_price = VALUES(open_price),
    high_price = VALUES(high_price),
    low_price = VALUES(low_price),
    current_price = VALUES(current_price),
    volume = VALUES(volume),
    latest_trading_day = VALUES(latest_trading_day),
    previous_close = VALUES(previous_close),
    change_amount = VALUES(change_amount),
    change_percent = VALUES(change_percent),
    updated_at = CURRENT_TIMESTAMP;

-- =====================================================
-- SETUP USER BALANCES
-- =====================================================
-- Ensure default users have cash balances for testing
INSERT IGNORE INTO user_balance (user_id, cash_balance) VALUES 
    ('default_user', 10000.00),
    ('test_user', 10000.00),
    ('demo_user', 25000.00),
    ('team_user_1', 15000.00),
    ('team_user_2', 15000.00),
    ('team_user_3', 15000.00);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Check how many stocks were inserted
SELECT 
    COUNT(*) as total_stocks,
    MIN(current_price) as min_price,
    MAX(current_price) as max_price,
    AVG(current_price) as avg_price
FROM api_stock_information;

-- Show sample of inserted data
SELECT 
    stock_symbol,
    current_price,
    volume,
    CONCAT('+', change_amount) as change_amount,
    CONCAT(change_percent, '%') as change_percent,
    updated_at
FROM api_stock_information 
ORDER BY current_price DESC 
LIMIT 10;

-- Check user balances
SELECT user_id, cash_balance, updated_at 
FROM user_balance 
ORDER BY user_id;

-- Summary for confirmation
SELECT 'DATA POPULATION COMPLETED' as status,
       (SELECT COUNT(*) FROM api_stock_information) as stocks_loaded,
       (SELECT COUNT(*) FROM user_balance) as users_created;

-- =====================================================
-- OPTIONAL: CREATE SAMPLE PORTFOLIO FOR DEMO
-- =====================================================
-- Uncomment the following section if you want to create
-- a sample portfolio with some holdings for demonstration

/*
-- Sample trades for demo_user
INSERT INTO trades (stock_symbol, trade_type, price_at_trade, quantity, trade_date) VALUES
    ('AAPL', 'BUY', 207.57, 50, '2025-07-25 10:30:00'),
    ('MSFT', 'BUY', 418.50, 25, '2025-07-26 14:15:00'),
    ('GOOGL', 'BUY', 2750.00, 5, '2025-07-27 11:45:00'),
    ('NVDA', 'BUY', 875.25, 15, '2025-07-28 09:20:00'),
    ('TSLA', 'BUY', 248.50, 20, '2025-07-29 16:10:00');

-- Sample holdings for demo_user (calculated from trades above)
INSERT INTO holdings (stock_symbol, quantity, average_cost) VALUES
    ('AAPL', 50, 207.57),
    ('MSFT', 25, 418.50),
    ('GOOGL', 5, 2750.00),
    ('NVDA', 15, 875.25),
    ('TSLA', 20, 248.50);

-- Update demo_user cash balance (subtract total cost of purchases)
-- Total cost: (50*207.57) + (25*418.50) + (5*2750.00) + (15*875.25) + (20*248.50) = $47,986.25
UPDATE user_balance 
SET cash_balance = 25000.00 - 47986.25 
WHERE user_id = 'demo_user';
*/

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================
SELECT 
    '✅ TEST DATA POPULATION COMPLETED!' as message,
    'You can now run trading tests and operations.' as instruction,
    'Use the following test accounts:' as accounts,
    'default_user, test_user, demo_user, team_user_1, team_user_2, team_user_3' as user_list;
