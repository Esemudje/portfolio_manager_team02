import mysql.connector
import datetime
from .buyRequest import buyRequest

def buy_stock(buy_request: buyRequest, database: str, cash: float) -> str:
    db = None

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@Dragonoid12",
            database=database
        )

        cursor = db.cursor(dictionary=True)

        # Get current stock price
        cursor.execute(
            "SELECT current_price FROM api_stock_information WHERE stock_symbol = %s",
            (buy_request.symbol,)
        )
        result = cursor.fetchone()

        if not result:
            return 'Symbol not found...'

        price = float(result['current_price'])
        total_cost = price * buy_request.quantity

        if cash < total_cost:
            return 'Insufficient Funds...'

        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert into trades
        cursor.execute(
            "INSERT INTO trades (stock_symbol, trade_type, price_at_trade, quantity, trade_date) VALUES (%s, %s, %s, %s, %s)",
            (buy_request.symbol, "BUY", price, buy_request.quantity, date_time)
        )
        db.commit()

        trade_id = cursor.lastrowid
        print(f"Trade successful. Trade ID: {trade_id}")

        # Check holdings
        cursor.execute(
            "SELECT quantity, average_cost FROM holdings WHERE stock_symbol = %s",
            (buy_request.symbol,)
        )
        results = cursor.fetchall()

        if results:
            # Update existing holding
            existing_quantity = int(results[0]['quantity'])
            existing_avg_cost = float(results[0]['average_cost'])

            new_quantity = existing_quantity + buy_request.quantity
            new_avg_cost = (
                (existing_quantity * existing_avg_cost) + (buy_request.quantity * price)
            ) / new_quantity

            cursor.execute(
                "UPDATE holdings SET quantity = %s, average_cost = %s WHERE stock_symbol = %s",
                (new_quantity, new_avg_cost, buy_request.symbol)
            )
            print("Holding Updated")
        else:
            # Insert new holding
            cursor.execute(
                "INSERT INTO holdings (stock_symbol, quantity, average_cost) VALUES (%s, %s, %s)",
                (buy_request.symbol, buy_request.quantity, price)
            )

            print("Holding added")

        db.commit()

    except mysql.connector.Error as err:
        if db:
            db.rollback()
        return "Database error"

    finally:
        if db:
            db.close()

    return "Transaction successful. Your portfolio will be updated momentarily"
