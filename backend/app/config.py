import os
from dotenv import load_dotenv

load_dotenv()  # reads .env to add database and API key configurations

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Parse comma-separated API keys
    ALPHA_VANTAGE_KEYS = [key.strip() for key in os.getenv("ALPHA_VANTAGE_KEY", "").split(",") if key.strip()]
    # Keep single key for backward compatibility (uses first key)
    ALPHA_VANTAGE_KEY = ALPHA_VANTAGE_KEYS[0] if ALPHA_VANTAGE_KEYS else None
