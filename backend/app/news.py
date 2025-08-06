
import mysql.connector
from dotenv import load_dotenv
import os

from flask import jsonify

load_dotenv()



#connect to db
def get_db_connection():
    """Get database connection using environment variables"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )

        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


#get headlines from database
def get_headlines():
    db = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT headline, reported_by FROM news")
        results = cursor.fetchall() #results is a list of tuples ( [(headline1), (reporter1)])

        return results

    except Exception as e:
        print(f'Error retrieving from database: {e}')
        return {"error": str(e)}
    finally:
        if db:
            db.close()