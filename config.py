import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for Flask application"""

    # Flask configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
    )
    PORT = int(os.environ.get("PORT", 5000))

    # Security configuration
    BCRYPT_LOG_ROUNDS = int(os.environ.get("BCRYPT_LOG_ROUNDS", 12))

    # Database configuration
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"postgresql://{os.environ.get('DB_USER', 'username')}:{os.environ.get('DB_PASSWORD', 'password')}@"
        f"{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/"
        f"{os.environ.get('DB_NAME', 'ledgerflow_db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # API Keys for external services
    FREE_CURRENCY_API_KEY = os.environ.get("FREE_CURRENCY_API_KEY")
    BING_NEWS_API_KEY = os.environ.get("BING_NEWS_API_KEY")

    # API URLs
    FREE_CURRENCY_API_URL = "https://api.freecurrencyapi.com/v1/latest"
    FRANKFURTER_API_URL = "https://api.frankfurter.app/latest"
    BING_NEWS_API_URL = "https://api.bing.microsoft.com/v7.0/news/search"

    # Obtener orígenes CORS como lista
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "")
    if CORS_ORIGINS:
        CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS.split(",")]
    else:
        CORS_ORIGINS = []
