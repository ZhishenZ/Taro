import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from taro.db.models import Base

def get_database_url():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        host = os.getenv('DB_HOST', 'postgres')
        port = os.getenv('DB_PORT', '5432')
        name = os.getenv('DB_NAME', 'taro_stock')
        user = os.getenv('DB_USER', 'taro_user')
        password = os.getenv('DB_PASSWORD', 'taro_password')
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return database_url

engine = create_engine(get_database_url())
Session = sessionmaker(bind=engine)
