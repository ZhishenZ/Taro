from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TradeDate(Base):
    __tablename__ = "trade_date"
    trade_date_id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    trade_date = Column(Date, nullable=False)

class Company(Base):
    __tablename__ = "company"
    company_id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    company_ticker = Column(String(10), nullable=False)  # FK to Company.ticker (has not been implemented yet)

class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    __table_args__ = (UniqueConstraint('trade_date_id', 'company_id'),)
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    trade_date_id = Column(Integer, ForeignKey("trade_date.trade_date_id"))
    company_id = Column(Integer, ForeignKey("company.company_id"))
    fundamentals = relationship("Fundamentals", back_populates="daily_metrics", uselist=False)

class Fundamentals(Base):
    __tablename__ = "fundamentals"
    daily_metrics_id = Column(Integer, ForeignKey("daily_metrics.id"), primary_key=True)
    open_price = Column(Numeric(10, 2), nullable=False)
    high_price = Column(Numeric(10, 2), nullable=False)
    close_price = Column(Numeric(10, 2), nullable=False)
    low_price = Column(Numeric(10, 2), nullable=False)
    volume = Column(Numeric(10, 2), nullable=False)
    daily_metrics = relationship("DailyMetrics", back_populates="fundamentals")
