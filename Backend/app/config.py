import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Database Configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "xtraMiles")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
HOST = os.getenv("HOST","localhost")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"



# JWT Authentication Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
EXP_TIME = int(os.getenv("EXP_TIME", 60))  # Token expiration time in minutes
