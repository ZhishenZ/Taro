"""
Essential tests for Taro database system.
Following the blog recommendations for clean, focused testing.
"""

import pytest
import subprocess
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from taro.paths import Taro_path

class TestDatabase:
    """Essential database tests."""

    def test_connection(self, database_url):
        """Test basic database connection."""
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_models_import(self):
        """Test that models can be imported successfully."""
        from taro.db.models import Base, DailyMetrics, Fundamentals

        assert Base is not None
        assert DailyMetrics is not None
        assert Fundamentals is not None

        # Verify tables are available in metadata
        tables = Base.metadata.tables
        assert len(tables) >= 2

        # Models now use default (public) schema, so schema should be None
        for table_name, table in tables.items():
            assert table.schema is None or table.schema == 'public'

    def test_schema_exists(self, database_url):
        """Test that public schema exists in database (default schema)."""
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'public'")
            )
            schema_exists = result.fetchone() is not None
            assert schema_exists, "Public schema does not exist in database"

    def test_tables_exist(self, database_url):
        """Test that all model tables exist in database."""
        from taro.db.models import Base

        engine = create_engine(database_url)
        inspector = inspect(engine)

        # Get tables in public schema (default schema)
        db_tables = set(inspector.get_table_names())

        # Get model table names dynamically
        model_tables = set(table.name for table in Base.metadata.tables.values())

        # Check all model tables exist in database
        for table_name in model_tables:
            assert table_name in db_tables, f"Model table {table_name} does not exist in public schema"

        # Verify we have the expected number of tables
        assert len(model_tables) > 0, "No model tables found"
        assert len(db_tables) >= len(model_tables), f"Database has fewer tables than models: DB={db_tables}, Models={model_tables}"

    def test_table_structure(self, database_url):
        """Test that model tables have the correct columns and types based on SQLAlchemy models."""
        from taro.db.models import Base
        from sqlalchemy import Integer, String, Date, Numeric, ForeignKey

        engine = create_engine(database_url)
        inspector = inspect(engine)

        # Test each model table dynamically
        for table_key, table in Base.metadata.tables.items():
            table_name = table.name
            # Get database columns from public schema (default)
            db_columns = inspector.get_columns(table_name)
            db_column_names = {col['name'] for col in db_columns}

            # Get model columns
            model_columns = {col.name for col in table.columns}

            # Verify all model columns exist in database
            assert model_columns.issubset(db_column_names), (
                f"Table {table_name}: Model columns {model_columns - db_column_names} "
                f"missing from database. DB has: {db_column_names}"
            )

            # Create a mapping of db column info for detailed validation
            db_col_info = {col['name']: col for col in db_columns}

            # Dynamically verify column types and constraints
            for col in table.columns:
                if col.name in db_col_info:
                    db_col = db_col_info[col.name]
                    db_type = str(db_col['type']).upper()

                    # Dynamic type validation based on SQLAlchemy column type
                    if isinstance(col.type, Integer):
                        assert any(t in db_type for t in ['INTEGER', 'BIGINT', 'SERIAL']), (
                            f"Table {table_name}, column {col.name}: expected integer type, got {db_type}"
                        )
                    elif isinstance(col.type, String):
                        assert any(t in db_type for t in ['VARCHAR', 'TEXT', 'CHAR']), (
                            f"Table {table_name}, column {col.name}: expected string type, got {db_type}"
                        )
                    elif isinstance(col.type, (Numeric)):
                        assert any(t in db_type for t in ['NUMERIC', 'DECIMAL', 'REAL', 'FLOAT', 'DOUBLE']), (
                            f"Table {table_name}, column {col.name}: expected numeric type, got {db_type}"
                        )
                    elif isinstance(col.type, Date):
                        assert any(t in db_type for t in ['DATE', 'TIMESTAMP']), (
                            f"Table {table_name}, column {col.name}: expected date type, got {db_type}"
                        )

                    # Verify nullable constraints match model definition
                    model_nullable = col.nullable
                    db_nullable = db_col['nullable']
                    assert model_nullable == db_nullable, (
                        f"Table {table_name}, column {col.name}: nullable mismatch. "
                        f"Model: {model_nullable}, DB: {db_nullable}"
                    )

                    # Verify primary key constraints
                    if col.primary_key:
                        pk_constraint = inspector.get_pk_constraint(table_name)
                        db_pk_columns = set(pk_constraint['constrained_columns']) if pk_constraint['constrained_columns'] else set()
                        assert col.name in db_pk_columns, (
                            f"Table {table_name}, column {col.name}: should be primary key but isn't in DB"
                        )

            # Verify foreign key relationships
            db_fks = inspector.get_foreign_keys(table_name)
            model_fks = [col for col in table.columns if col.foreign_keys]

            db_fk_columns = {fk['constrained_columns'][0] for fk in db_fks if fk['constrained_columns']}
            model_fk_columns = {col.name for col in model_fks}

            assert model_fk_columns == db_fk_columns, (
                f"Table {table_name}: Foreign key columns mismatch. "
                f"Model: {model_fk_columns}, DB: {db_fk_columns}"
            )

    def test_models_match_database(self, database_url):
        """Test that SQLAlchemy models match actual database schema."""
        from taro.db.models import Base

        engine = create_engine(database_url)
        inspector = inspect(engine)

        # Get model table names
        model_tables = set(table.name for table in Base.metadata.tables.values())

        # Get database table names in public schema (default), excluding system tables
        all_db_tables = set(inspector.get_table_names())
        # Filter out alembic_version and other system tables
        db_tables = {t for t in all_db_tables if t not in ['alembic_version']}

        assert model_tables.issubset(db_tables), f"Model tables {model_tables} not found in database tables {db_tables}"

    def test_alembic_current_version(self):
        """Test that Alembic has a current version."""
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            cwd=Taro_path
        )
        assert result.returncode == 0

        # Should have some output indicating current version
        assert result.stdout.strip() != "", "Alembic should show current version"

    def test_alembic_check_no_pending(self):
        """Test that there are no pending migrations."""
        result = subprocess.run(
            ["alembic", "check"],
            capture_output=True,
            text=True,
            cwd=Taro_path
        )
        assert result.returncode == 0
        assert "No new upgrade operations detected" in result.stdout

    def test_alembic_history(self):
        """Test alembic history shows migrations."""
        result = subprocess.run(
            ["alembic", "history"],
            capture_output=True,
            text=True,
            cwd=Taro_path
        )
        assert result.returncode == 0

    def test_database_crud_operations(self, database_url):
        """Test basic CRUD operations work with actual model structure."""
        from taro.db.models import Base, DailyMetrics, Fundamentals
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import Integer, String, Date, Numeric
        from datetime import date
        import uuid

        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)

        with Session() as session:
            # Dynamically create test data based on model structure
            dm_table = Base.metadata.tables.get('daily_metrics')
            dm_kwargs = {}

            # Generate unique test identifier to avoid conflicts
            test_id = str(uuid.uuid4())[:8]            # Populate DailyMetrics with appropriate test values based on column types
            for col in dm_table.columns:
                if not col.primary_key and not col.foreign_keys:  # Skip auto-generated and FK columns
                    if isinstance(col.type, Date):
                        dm_kwargs[col.name] = date(2024, 1, 1)
                    elif isinstance(col.type, String):
                        # Respect column length constraints
                        max_length = getattr(col.type, 'length', None)
                        if max_length:
                            # Use shorter unique value that fits in the column
                            value = f"T{test_id}"[:max_length]
                        else:
                            value = f"TEST_{test_id}"
                        dm_kwargs[col.name] = value
                    elif isinstance(col.type, Integer):
                        dm_kwargs[col.name] = 12345
                    elif isinstance(col.type, Numeric):
                        dm_kwargs[col.name] = 123.45

            # Create DailyMetrics instance
            dm = DailyMetrics(**dm_kwargs)
            session.add(dm)
            session.flush()  # Get the ID

            # Dynamically create Fundamentals test data
            fund_table = Base.metadata.tables.get('fundamentals')
            fund_kwargs = {}

            for col in fund_table.columns:
                if not col.primary_key:  # Include FK columns but skip auto-generated primary keys
                    if col.foreign_keys:
                        # This is a foreign key - use the DailyMetrics ID
                        fund_kwargs[col.name] = dm.id
                    elif isinstance(col.type, Numeric):
                        # Generate different test values for different price/volume fields
                        if 'open' in col.name.lower():
                            fund_kwargs[col.name] = 100.50
                        elif 'high' in col.name.lower():
                            fund_kwargs[col.name] = 110.75
                        elif 'close' in col.name.lower():
                            fund_kwargs[col.name] = 105.25
                        elif 'low' in col.name.lower():
                            fund_kwargs[col.name] = 95.80
                        elif 'volume' in col.name.lower():
                            fund_kwargs[col.name] = 50000.00
                        else:
                            fund_kwargs[col.name] = 100.00  # Default numeric value
                    elif isinstance(col.type, Date):
                        fund_kwargs[col.name] = date(2024, 1, 1)
                    elif isinstance(col.type, String):
                        # Respect column length constraints
                        max_length = getattr(col.type, 'length', None)
                        if max_length:
                            value = f"T{test_id}"[:max_length]
                        else:
                            value = f"TEST_{test_id}"
                        fund_kwargs[col.name] = value
                    elif isinstance(col.type, Integer):
                        fund_kwargs[col.name] = 1000

            # Create Fundamentals instance
            fund = Fundamentals(**fund_kwargs)
            session.add(fund)
            session.commit()

            # Test SELECT - dynamically verify all non-auto fields
            string_filters = {k: v for k, v in dm_kwargs.items() if isinstance(v, str)}
            retrieved_dm = session.query(DailyMetrics).filter_by(**string_filters).first()
            assert retrieved_dm is not None

            # Verify all set attributes match
            for attr_name, expected_value in dm_kwargs.items():
                actual_value = getattr(retrieved_dm, attr_name)
                assert actual_value == expected_value, f"DailyMetrics.{attr_name}: expected {expected_value}, got {actual_value}"

            # Test Fundamentals SELECT and verify FK relationship
            retrieved_fund = session.query(Fundamentals).filter_by(daily_metrics_id=dm.id).first()
            assert retrieved_fund is not None
            assert retrieved_fund.daily_metrics_id == dm.id

            # Dynamically verify Fundamentals attributes
            from decimal import Decimal
            for attr_name, expected_value in fund_kwargs.items():
                if not attr_name.endswith('_id') or attr_name == 'daily_metrics_id':  # Verify all including FK
                    actual_value = getattr(retrieved_fund, attr_name)

                    # Handle Decimal comparison for numeric fields
                    if isinstance(actual_value, Decimal) and isinstance(expected_value, (int, float)):
                        actual_value = float(actual_value)
                    elif isinstance(expected_value, Decimal) and isinstance(actual_value, (int, float)):
                        expected_value = float(expected_value)

                    assert actual_value == expected_value, f"Fundamentals.{attr_name}: expected {expected_value}, got {actual_value}"

            # Test relationship access if it exists
            if hasattr(retrieved_dm, 'fundamentals'):
                assert retrieved_dm.fundamentals is not None
                # Verify relationship points to the correct fundamentals record
                related_fund = retrieved_dm.fundamentals
                assert related_fund.id == retrieved_fund.id

            # Test UPDATE - modify some non-key fields
            update_fields = {}
            for col in dm_table.columns:
                if not col.primary_key and not col.foreign_keys and isinstance(col.type, String):
                    max_length = getattr(col.type, 'length', None)
                    if max_length:
                        new_value = f"U{test_id}"[:max_length]
                    else:
                        new_value = f"UPDATED_{test_id}"
                    update_fields[col.name] = new_value
                    setattr(retrieved_dm, col.name, new_value)

            # Update a numeric field in Fundamentals
            numeric_field = None
            for col in fund_table.columns:
                if isinstance(col.type, Numeric) and 'close' in col.name.lower():
                    numeric_field = col.name
                    setattr(retrieved_fund, col.name, 999.99)
                    break

            session.commit()

            # Verify updates
            if update_fields:
                updated_dm = session.query(DailyMetrics).filter_by(**update_fields).first()
                assert updated_dm is not None
                for field_name, expected_value in update_fields.items():
                    actual_value = getattr(updated_dm, field_name)
                    assert actual_value == expected_value

            if numeric_field:
                updated_fund = session.query(Fundamentals).filter_by(daily_metrics_id=dm.id).first()
                actual_value = getattr(updated_fund, numeric_field)
                # Handle Decimal comparison
                if isinstance(actual_value, Decimal):
                    actual_value = float(actual_value)
                assert actual_value == 999.99

            # Test DELETE (cleanup)
            session.delete(retrieved_fund)
            session.delete(retrieved_dm)
            session.commit()


class TestMigrations:
    """Test migration system functionality."""

    def test_migration_files_exist(self):
        """Test that migration files exist."""
        versions_dir = Path(Taro_path/"src/taro/migrations/versions")
        migration_files = list(versions_dir.glob("*.py"))
        assert len(migration_files) > 0, "No migration files found"

    def test_alembic_version_table(self, database_url):
        """Test that alembic_version table exists and has current version."""
        engine = create_engine(database_url)
        with engine.connect() as connection:
            # Check table exists
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'alembic_version'
                )
            """))
            assert result.fetchone()[0], "alembic_version table does not exist"

            # Check has current version
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            assert version is not None, "No current version in alembic_version table"
            assert version[0] is not None, "Current version is None"
