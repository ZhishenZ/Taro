"""Alembic environment configuration for PostgreSQL database schema."""

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import models from shared db location
from taro.db.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use db models metadata for unified schema
target_metadata = Base.metadata


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


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Override the sqlalchemy.url with environment variables
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
