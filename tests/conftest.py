"""
Pytest configuration and fixtures for Taro tests.
"""

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

from taro.utils import get_database_url


@pytest.fixture(scope="session")
def database_url():
    """Get database URL from environment variables."""
    return get_database_url()
