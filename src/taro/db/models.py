from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    __table_args__ = (UniqueConstraint('trade_date', 'ticker'),)
    id = Column(Integer, primary_key=True)
    trade_date = Column(Date, nullable=False)
    ticker = Column(String(10), nullable=False)
    fundamentals = relationship("Fundamentals", back_populates="daily_metrics", uselist=False)

class Fundamentals(Base):
    __tablename__ = "fundamentals"
    id = Column(Integer, primary_key=True)
    daily_metrics_id = Column(Integer, ForeignKey("daily_metrics.id"), unique=True, nullable=False)
    open_price = Column(Numeric(10, 2), nullable=False)
    high_price = Column(Numeric(10, 2), nullable=False)
    close_price = Column(Numeric(10, 2), nullable=False)
    low_price = Column(Numeric(10, 2), nullable=False)
    volume = Column(Numeric(10, 2), nullable=False)
    daily_metrics = relationship("DailyMetrics", back_populates="fundamentals")
