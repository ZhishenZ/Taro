import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from models import Base
from dotenv import load_dotenv

# Load environment variables from a .env file.
# The .env file should be in the same directory as this script.
# If the .env file is elsewhere, specify its path
load_dotenv()


db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT", "5432")
db_name = os.environ.get("DB_NAME", "tarodb")

missing = []
if not db_user:
    missing.append("DB_USER")
if not db_password:
    missing.append("DB_PASSWORD")
if not db_host:
    missing.append("DB_HOST")
if not db_name:
    missing.append("DB_NAME")
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")
except SQLAlchemyError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")