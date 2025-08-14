"""
Pytest configuration and fixtures for Taro tests.
"""

import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
src_path = Path(__file__).parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def database_url():
    """Get database URL from environment variables."""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    host = os.getenv('DB_HOST', 'postgres')
    port = os.getenv('DB_PORT', '5432')
    name = os.getenv('DB_NAME', 'taro_stock')
    user = os.getenv('DB_USER', 'taro_user')
    password = os.getenv('DB_PASSWORD', 'taro_password')

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"
