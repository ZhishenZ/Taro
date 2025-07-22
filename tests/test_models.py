import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from taro.db.models import Base, DailyMetrics, Fundamentals
from datetime import date
from tests.db_config import DB_PARAMS


@pytest.fixture
def sqlalchemy_engine():
    """Create SQLAlchemy engine for PostgreSQL test DB"""
    connection_string = f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}"
    engine = create_engine(connection_string)
    # Create all tables
    Base.metadata.create_all(engine)
    yield engine
    # Drop all tables after test
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(sqlalchemy_engine):
    """Create DB session"""
    Session = sessionmaker(bind=sqlalchemy_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

def test_tables_created(sqlalchemy_engine):
    """Test if tables are created successfully"""
    from sqlalchemy import inspect
    inspector = inspect(sqlalchemy_engine)
    tables = inspector.get_table_names()
    assert "daily_metrics" in tables, "daily_metrics table not created"
    assert "fundamentals" in tables, "fundamentals table not created"

def test_daily_metrics_columns(sqlalchemy_engine):
    """Test DailyMetrics table columns"""
    from sqlalchemy import inspect
    inspector = inspect(sqlalchemy_engine)
    columns = {col['name']: col for col in inspector.get_columns('daily_metrics')}
    assert 'id' in columns, "Missing id column"
    assert 'trade_date' in columns, "Missing trade_date column"
    assert 'ticker' in columns, "Missing ticker column"
    # Check ticker column length
    ticker_col = columns['ticker']
    assert ticker_col['type'].length == 10, "ticker column length is not 10"

def test_fundamentals_columns(sqlalchemy_engine):
    """Test Fundamentals table columns"""
    from sqlalchemy import inspect
    inspector = inspect(sqlalchemy_engine)
    columns = {col['name']: col for col in inspector.get_columns('fundamentals')}
    assert 'id' in columns, "Missing id column"
    assert 'daily_metrics_id' in columns, "Missing daily_metrics_id column"
    assert 'open_price' in columns, "Missing open_price column"
    assert 'high_price' in columns, "Missing high_price column"
    assert 'low_price' in columns, "Missing low_price column"
    assert 'close_price' in columns, "Missing close_price column"
    assert 'volume' in columns, "Missing volume column"

def test_unique_constraint(db_session):
    """Test unique constraint on (trade_date, ticker)"""
    dm1 = DailyMetrics(trade_date=date(2024, 1, 1), ticker="AAPL")
    db_session.add(dm1)
    db_session.commit()
    dm2 = DailyMetrics(trade_date=date(2024, 1, 1), ticker="AAPL")
    db_session.add(dm2)
    # Should raise unique constraint violation
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()

def test_relationship_mapping(db_session):
    """Test relationship mapping between DailyMetrics and Fundamentals"""
    dm = DailyMetrics(trade_date=date(2024, 1, 1), ticker="AAPL")
    db_session.add(dm)
    db_session.flush()  # Get ID
    fund = Fundamentals(
        daily_metrics_id=dm.id,
        open_price=100.00,
        high_price=110.00,
        low_price=95.00,
        close_price=105.00,
        volume=1000000.00
    )
    db_session.add(fund)
    db_session.commit()
    assert dm.fundamentals is not None, "DailyMetrics has no related Fundamentals"
    assert fund.daily_metrics is not None, "Fundamentals has no related DailyMetrics"
    assert fund.daily_metrics.id == dm.id, "Relationship mapping error"

def test_data_types(db_session):
    """Test data types for Fundamentals fields"""
    dm = DailyMetrics(trade_date=date(2024, 1, 1), ticker="AAPL")
    db_session.add(dm)
    db_session.flush()
    fund = Fundamentals(
        daily_metrics_id=dm.id,
        open_price=100.50,
        high_price=110.75,
        low_price=95.25,
        close_price=105.00,
        volume=1000000.50
    )
    db_session.add(fund)
    db_session.commit()
    saved_fund = db_session.query(Fundamentals).filter_by(daily_metrics_id=dm.id).first()
    assert saved_fund.open_price == 100.50
    assert saved_fund.volume == 1000000.50

def test_foreign_key_constraint(db_session):
    """Test foreign key constraint for Fundamentals.daily_metrics_id"""
    fund = Fundamentals(
        daily_metrics_id=99999,  # Non-existent ID
        open_price=100.00,
        high_price=110.00,
        low_price=95.00,
        close_price=105.00,
        volume=1000000.00
    )
    db_session.add(fund)
    # Should raise foreign key constraint violation
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()

def test_nullable_constraints(db_session):
    """Test NOT NULL constraints for DailyMetrics"""
    dm_incomplete = DailyMetrics()  # Missing trade_date and ticker
    db_session.add(dm_incomplete)
    # Should raise NOT NULL constraint violation
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback() 