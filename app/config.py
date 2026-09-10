import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "..", ".env"))


class Config:
    #SECRET_KEY = os.getenv("SECRET_KEY")
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-dev-secret-key-modify-for-production') # fallback key for development purpose - delete this line and uncomment above line
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")

    #In production use python -c "import secrets; print(secrets.token_hex(32))" to generate and set SECRET_KEY as environment variable
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", 'fallback-dev-secret-key-modify-for-production') # SECRET_KEY) #Replace fallback key with 'SECRET-KEY'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "12"))
    )
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
    JWT_COOKIE_CSRF_PROTECT = (
        os.getenv("JWT_COOKIE_CSRF_PROTECT", "false").lower() == "true"
    )
    JWT_CSRF_IN_COOKIES = True

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///crm.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
