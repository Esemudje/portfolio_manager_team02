

USE portfolio_manager;

-- Clear existing test data (optional - remove if you want to keep existing data)
-- DELETE FROM api_stock_information;
-- DELETE FROM holdings;
-- DELETE FROM trades;

-- =====================================================
-- POPULATE STOCK INFORMATION TABLE (TOP 30 STOCKS)
-- =====================================================
-- Insert or update stock data for top 30 companies
INSERT INTO api_stock_information (
    stock_symbol, open_price, high_price, low_price, current_price,
    volume, latest_trading_day, previous_close, change_amount, change_percent
) VALUES 
    -- Tech Giants
    ('AAPL', 209.05, 209.50, 207.10, 207.57, 45000000, '2025-08-06', 209.05, -1.48, -0.71),
    ('MSFT', 420.00, 421.00, 417.50, 418.50, 25000000, '2025-08-06', 419.20, -0.70, -0.17),
    ('GOOGL', 135.50, 136.00, 134.20, 135.75, 1200000, '2025-08-06', 136.20, -0.45, -0.33),
    ('AMZN', 185.00, 186.50, 184.20, 185.80, 8000000, '2025-08-06', 185.50, 0.30, 0.16),
    ('META', 497.00, 498.50, 494.00, 495.75, 18000000, '2025-08-06', 496.20, -0.45, -0.09),
    ('TSLA', 250.00, 252.00, 247.00, 248.50, 45000000, '2025-08-06', 250.00, -1.50, -0.60),
    
    -- AI & Semiconductor
    ('NVDA', 125.50, 127.00, 124.80, 126.25, 35000000, '2025-08-06', 125.90, 0.35, 0.28),
    ('AMD', 155.20, 157.00, 154.50, 156.80, 25000000, '2025-08-06', 155.90, 0.90, 0.58),
    ('INTC', 34.20, 34.80, 33.90, 34.50, 40000000, '2025-08-06', 34.10, 0.40, 1.17),
    ('CRM', 287.50, 289.00, 286.20, 288.40, 3200000, '2025-08-06', 287.80, 0.60, 0.21),
    ('ORCL', 138.90, 140.50, 138.20, 139.75, 8500000, '2025-08-06', 139.10, 0.65, 0.47),
    
    -- Financial Services
    ('JPM', 216.50, 217.00, 215.20, 215.80, 12000000, '2025-08-06', 216.30, -0.50, -0.23),
    ('BAC', 42.80, 43.20, 42.50, 42.90, 35000000, '2025-08-06', 42.75, 0.15, 0.35),
    ('WFC', 58.90, 59.50, 58.40, 59.20, 18000000, '2025-08-06', 58.80, 0.40, 0.68),
    ('GS', 485.00, 488.00, 482.00, 486.50, 2500000, '2025-08-06', 484.20, 2.30, 0.47),
    ('MS', 112.30, 113.80, 111.90, 113.20, 6200000, '2025-08-06', 112.50, 0.70, 0.62),
    
    -- Payment Networks & Fintech
    ('V', 286.00, 287.00, 284.50, 285.40, 5500000, '2025-08-06', 285.90, -0.50, -0.17),
    ('MA', 478.50, 480.00, 476.80, 479.20, 3200000, '2025-08-06', 478.90, 0.30, 0.06),
    ('PYPL', 78.90, 80.20, 78.40, 79.85, 12000000, '2025-08-06', 79.20, 0.65, 0.82),
    
    -- Healthcare & Pharma
    ('JNJ', 165.80, 166.50, 165.20, 166.10, 8500000, '2025-08-06', 165.70, 0.40, 0.24),
    ('PFE', 28.90, 29.40, 28.70, 29.15, 45000000, '2025-08-06', 28.85, 0.30, 1.04),
    ('UNH', 525.00, 528.00, 522.50, 526.80, 3800000, '2025-08-06', 524.20, 2.60, 0.50),
    ('ABBV', 176.50, 177.80, 175.90, 177.20, 7200000, '2025-08-06', 176.80, 0.40, 0.23),
    ('LLY', 789.20, 792.50, 786.80, 790.90, 1800000, '2025-08-06', 788.40, 2.50, 0.32),
    
    -- Consumer & Retail
    ('WMT', 168.90, 169.80, 168.20, 169.45, 12000000, '2025-08-06', 168.75, 0.70, 0.41),
    ('HD', 385.20, 387.50, 383.80, 386.90, 4500000, '2025-08-06', 385.60, 1.30, 0.34),
    ('NKE', 82.40, 83.20, 81.90, 82.85, 8500000, '2025-08-06', 82.50, 0.35, 0.42),
    ('MCD', 295.50, 297.20, 294.80, 296.40, 3100000, '2025-08-06', 295.90, 0.50, 0.17),
    ('COST', 878.90, 882.50, 876.20, 880.75, 1200000, '2025-08-06', 879.30, 1.45, 0.16),
    
    -- Berkshire Hathaway
    ('BRK.B', 435.20, 437.80, 434.50, 436.90, 3500000, '2025-08-06', 435.85, 1.05, 0.24)

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
-- POPULATE HOLDINGS TABLE (FAKE PORTFOLIO DATA)
-- =====================================================
-- Insert fake holdings for demonstration/fallback
INSERT INTO holdings (stock_symbol, quantity, average_cost) VALUES
    ('AAPL', 50.00, 195.50),      -- 50 shares at $195.50 avg cost
    ('MSFT', 25.00, 380.75),      -- 25 shares at $380.75 avg cost
    ('GOOGL', 100.00, 128.50),    -- 100 shares at $128.50 avg cost
    ('NVDA', 80.00, 118.30),      -- 80 shares at $118.30 avg cost
    ('TSLA', 30.00, 275.80),      -- 30 shares at $275.80 avg cost
    ('AMZN', 75.00, 172.25),      -- 75 shares at $172.25 avg cost
    ('META', 20.00, 465.90),      -- 20 shares at $465.90 avg cost
    ('JPM', 40.00, 198.40),       -- 40 shares at $198.40 avg cost
    ('V', 35.00, 270.60),         -- 35 shares at $270.60 avg cost
    ('JNJ', 60.00, 158.20),       -- 60 shares at $158.20 avg cost
    ('WMT', 45.00, 152.80),       -- 45 shares at $152.80 avg cost
    ('UNH', 12.00, 485.75),       -- 12 shares at $485.75 avg cost
    ('HD', 22.00, 365.40),        -- 22 shares at $365.40 avg cost
    ('COST', 5.00, 845.60),       -- 5 shares at $845.60 avg cost
    ('AMD', 55.00, 142.30)        -- 55 shares at $142.30 avg cost

ON DUPLICATE KEY UPDATE
    quantity = VALUES(quantity),
    average_cost = VALUES(average_cost),
    updated_at = CURRENT_TIMESTAMP;

-- =====================================================
-- POPULATE TRADES TABLE (FAKE TRANSACTION HISTORY)
-- =====================================================
-- Insert fake trade history to support the holdings
INSERT INTO trades (stock_symbol, trade_type, price_at_trade, quantity, trade_date) VALUES
    -- AAPL trades (50 total shares)
    ('AAPL', 'BUY', 185.20, 30.00, '2025-07-15 10:30:00'),
    ('AAPL', 'BUY', 210.80, 20.00, '2025-07-25 14:15:00'),
    
    -- MSFT trades (25 total shares)
    ('MSFT', 'BUY', 375.50, 15.00, '2025-07-10 09:45:00'),
    ('MSFT', 'BUY', 390.00, 10.00, '2025-07-20 11:20:00'),
    
    -- GOOGL trades (100 total shares)
    ('GOOGL', 'BUY', 125.00, 60.00, '2025-07-18 13:30:00'),
    ('GOOGL', 'BUY', 133.00, 40.00, '2025-07-28 15:45:00'),
    
    -- NVDA trades (80 total shares)
    ('NVDA', 'BUY', 115.50, 50.00, '2025-07-12 10:00:00'),
    ('NVDA', 'BUY', 122.60, 30.00, '2025-07-28 15:45:00'),
    
    -- TSLA trades (30 total shares)
    ('TSLA', 'BUY', 285.40, 20.00, '2025-07-08 12:15:00'),
    ('TSLA', 'BUY', 258.60, 10.00, '2025-07-22 09:30:00'),
    
    -- AMZN trades (75 total shares)
    ('AMZN', 'BUY', 168.25, 45.00, '2025-07-14 11:45:00'),
    ('AMZN', 'BUY', 178.25, 30.00, '2025-07-26 14:30:00'),
    
    -- META trades (20 total shares)
    ('META', 'BUY', 445.80, 12.00, '2025-07-16 10:20:00'),
    ('META', 'BUY', 495.00, 8.00, '2025-07-26 14:30:00'),
    
    -- JPM trades (40 total shares)
    ('JPM', 'BUY', 195.60, 25.00, '2025-07-09 09:15:00'),
    ('JPM', 'BUY', 202.80, 15.00, '2025-07-21 13:45:00'),
    
    -- V trades (35 total shares)
    ('V', 'BUY', 265.30, 20.00, '2025-07-11 10:45:00'),
    ('V', 'BUY', 278.90, 15.00, '2025-07-24 12:20:00'),
    
    -- JNJ trades (60 total shares)
    ('JNJ', 'BUY', 155.40, 35.00, '2025-07-13 11:30:00'),
    ('JNJ', 'BUY', 162.80, 25.00, '2025-07-27 14:15:00'),
    
    -- WMT trades (45 total shares)
    ('WMT', 'BUY', 148.60, 25.00, '2025-07-17 09:50:00'),
    ('WMT', 'BUY', 159.20, 20.00, '2025-07-29 13:25:00'),
    
    -- UNH trades (12 total shares)
    ('UNH', 'BUY', 485.75, 12.00, '2025-07-19 10:40:00'),
    
    -- HD trades (22 total shares)
    ('HD', 'BUY', 365.40, 22.00, '2025-07-23 11:55:00'),
    
    -- COST trades (5 total shares)
    ('COST', 'BUY', 845.60, 5.00, '2025-07-30 15:20:00'),
    
    -- AMD trades (55 total shares)
    ('AMD', 'BUY', 138.90, 30.00, '2025-07-05 10:15:00'),
    ('AMD', 'BUY', 147.20, 25.00, '2025-07-31 12:45:00');

-- Show summary after population
SELECT 
    'Stock Information' as table_name,
    COUNT(*) as record_count
FROM api_stock_information
UNION ALL
SELECT 
    'Holdings' as table_name,
    COUNT(*) as record_count
FROM holdings
UNION ALL
SELECT 
    'Trades' as table_name,
    COUNT(*) as record_count
FROM trades;

