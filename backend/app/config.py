import os
from dotenv import load_dotenv

load_dotenv()  # reads .env to add database and API key configurations

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
