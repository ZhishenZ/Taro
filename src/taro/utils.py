import os

def print_hi():
    print("hi")

def get_database_url():
    """Get PostgreSQL database URL from environment variables.

    Works in both development (Docker) and production/CI environments.
    """
    # Check for full DATABASE_URL first (common in CI/CD)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    # Fall back to individual components
    host = os.getenv('DB_HOST', 'postgres')  # Default to Docker service name
    port = os.getenv('DB_PORT', '5432')
    name = os.getenv('DB_NAME', 'taro_stock')
    user = os.getenv('DB_USER', 'taro_user')
    password = os.getenv('DB_PASSWORD', 'taro_password')

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"
