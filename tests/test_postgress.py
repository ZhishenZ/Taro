import os
import pytest
import psycopg2

# Database connection parameters
DB_PARAMS = {
    # Get the database host from the PG environment variable (used in GitHub CI); 
    # default to "postgres" if not set
    "host": os.environ.get("PG", "postgres"),
    "port": 5432,
    "user": "taro_user",
    "password": "taro_password",
    "dbname": "taro_stock"
}

@pytest.fixture
def db_connection():
    """Fixture to provide database connection"""
    conn = psycopg2.connect(**DB_PARAMS)
    yield conn
    conn.close()

def test_database_connection(db_connection):
    """Test database connection"""
    # Test if connection is established successfully
    assert db_connection is not None, "Database connection failed"
    assert not db_connection.closed, "Database connection is closed"

def test_database_version(db_connection):
    """Test database version query"""
    cur = db_connection.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    cur.close()
    
    # Verify version information
    assert version is not None, "Failed to get database version"
    assert "PostgreSQL" in version, f"Invalid version info: {version}"
    print(f"\nPostgreSQL version: {version}")

def test_database_query(db_connection):
    """Test basic database query"""
    cur = db_connection.cursor()
    
    # Test simple query
    cur.execute("SELECT 1 as test;")
    result = cur.fetchone()
    cur.close()
    
    # Verify query result
    assert result is not None, "Query returned empty result"
    assert result[0] == 1, f"Query result doesn't match expected value: {result[0]}"

@pytest.mark.parametrize("query,expected", [
    ("SELECT current_database();", "taro_stock"),
    ("SELECT current_user;", "taro_user"),
])
def test_database_info(db_connection, query, expected):
    """Test database information queries"""
    cur = db_connection.cursor()
    cur.execute(query)
    result = cur.fetchone()[0]
    cur.close()
    
    # Verify database information
    assert result == expected, f"Database info mismatch: expected {expected}, got {result}" 