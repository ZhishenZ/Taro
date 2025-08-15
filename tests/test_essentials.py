"""
Essential tests for Taro database system.
Following the blog recommendations for clean, focused testing.
"""

import pytest
import subprocess
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from taro.paths import Taro_dir

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
        from taro.db.models import Base, TradeDate, Company, DailyMetrics, Fundamentals

        assert Base is not None
        assert TradeDate is not None
        assert Company is not None
        assert DailyMetrics is not None
        assert Fundamentals is not None

        # Verify tables are available in metadata
        tables = Base.metadata.tables
        assert len(tables) >= 4  # trade_date, company, daily_metrics, fundamentals

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
            cwd=Taro_dir
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
            cwd=Taro_dir
        )
        assert result.returncode == 0
        assert "No new upgrade operations detected" in result.stdout

    def test_alembic_history(self):
        """Test alembic history shows migrations."""
        result = subprocess.run(
            ["alembic", "history"],
            capture_output=True,
            text=True,
            cwd=Taro_dir
        )
        assert result.returncode == 0

    def test_database_crud_operations(self, database_url):
        """Test basic CRUD operations work with actual model structure."""
        from taro.db.models import Base, TradeDate, Company, DailyMetrics, Fundamentals
        from sqlalchemy.orm import sessionmaker
        from datetime import date
        from decimal import Decimal

        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)

        with Session() as session:
            # CREATE: First create prerequisite TradeDate and Company records
            trade_date = TradeDate(trade_date=date(2024, 1, 15))
            session.add(trade_date)
            session.flush()  # Get the ID

            company = Company(company_ticker="TEST")
            session.add(company)
            session.flush()  # Get the ID

            # Create DailyMetrics with foreign keys
            dm = DailyMetrics(
                trade_date_id=trade_date.trade_date_id,
                company_id=company.company_id
            )
            session.add(dm)
            session.flush()  # Get the ID

            # Create Fundamentals with foreign key to DailyMetrics
            fund = Fundamentals(
                daily_metrics_id=dm.id,
                open_price=100.50,
                high_price=110.75,
                close_price=105.25,
                low_price=95.80,
                volume=50000
            )
            session.add(fund)
            session.commit()

            # READ: Test SELECT and verify data
            retrieved_trade_date = session.query(TradeDate).filter_by(
                trade_date_id=trade_date.trade_date_id
            ).first()
            assert retrieved_trade_date is not None
            assert retrieved_trade_date.trade_date == date(2024, 1, 15)

            retrieved_company = session.query(Company).filter_by(
                company_id=company.company_id
            ).first()
            assert retrieved_company is not None
            assert retrieved_company.company_ticker == "TEST"

            retrieved_dm = session.query(DailyMetrics).filter_by(id=dm.id).first()
            assert retrieved_dm is not None
            assert retrieved_dm.trade_date_id == trade_date.trade_date_id
            assert retrieved_dm.company_id == company.company_id

            # Test Fundamentals SELECT and verify FK relationship
            retrieved_fund = session.query(Fundamentals).filter_by(daily_metrics_id=dm.id).first()
            assert retrieved_fund is not None
            assert retrieved_fund.daily_metrics_id == dm.id

            # Verify Fundamentals values
            assert float(retrieved_fund.open_price) == 100.50
            assert float(retrieved_fund.high_price) == 110.75
            assert float(retrieved_fund.close_price) == 105.25
            assert float(retrieved_fund.low_price) == 95.80
            assert retrieved_fund.volume == 50000

            # Test relationship access
            assert retrieved_dm.fundamentals is not None
            assert retrieved_dm.fundamentals.daily_metrics_id == dm.id

            # UPDATE: Modify some fields
            retrieved_company.company_ticker = "UPDATED"
            retrieved_fund.close_price = 999.99
            session.commit()

            # Verify updates
            updated_company = session.query(Company).filter_by(company_id=company.company_id).first()
            assert updated_company.company_ticker == "UPDATED"

            updated_fund = session.query(Fundamentals).filter_by(daily_metrics_id=dm.id).first()
            assert float(updated_fund.close_price) == 999.99

            # DELETE: Clean up test data (must respect FK constraints)
            # Delete in order: fundamentals -> daily_metrics -> company/trade_date
            session.delete(retrieved_fund)
            session.commit()

            session.delete(retrieved_dm)
            session.commit()

            session.delete(retrieved_company)
            session.delete(retrieved_trade_date)
            session.commit()


class TestMigrations:
    """Test migration system functionality."""

    def test_migration_files_exist(self):
        """Test that migration files exist."""
        versions_dir = Path(Taro_dir/"src/taro/migrations/versions")
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
