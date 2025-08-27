import argparse
from datetime import datetime, timezone
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import declarative_base, sessionmaker

from taro.cli.sub_cli import SubCli
from taro.configs import close_utc_hour
from taro.fetcher.fetcher_yfinance import YFinanceFetcher
# from taro.migrations.env import get_database_url
from taro.utils import get_database_url
import taro.db.models as models

class TaroDailyCli(SubCli):
    def get_name(self):
        return "daily"

    def populate_subparser(self, subparser:argparse.ArgumentParser):
        subparser.add_argument("-t", "--ticker")
        subparser.add_argument("-d", "--date")
        subparser.add_argument("-u", "--update_database", action="store_true")

    def update_database(self, ticker, date, d):
        engine = create_engine(get_database_url())
        Session = sessionmaker(bind=engine)
        session = Session()

        company_exist_in_company_table = session.query(models.Company).filter(models.Company.company_ticker==ticker).first() is not None
        if not company_exist_in_company_table:
            new_company = models.Company(company_ticker = ticker)
            session.add(new_company)
            session.commit()

        date_exist_in_trade_date_table = session.query(models.TradeDate).filter(models.TradeDate.trade_date==date).first() is not None
        if not date_exist_in_trade_date_table:
            new_date = models.TradeDate(trade_date = date)
            session.add(new_date)
            session.commit()

        company_id = session.query(models.Company).filter(models.Company.company_ticker==ticker).first().company_id
        tradedate_id = session.query(models.TradeDate).filter(models.TradeDate.trade_date==date).first().trade_date_id

        company_date_pair_exist_in_table = session.query(models.DailyMetrics).filter(and_(models.DailyMetrics.company_id==company_id, models.DailyMetrics.trade_date_id==tradedate_id)).first() is not None
        if not company_date_pair_exist_in_table:
            new_company_date_pair = models.DailyMetrics(company_id = company_id, trade_date_id=tradedate_id)
            session.add(new_company_date_pair)
            session.commit()

        daily_metrics_id = session.query(models.DailyMetrics).filter(and_(models.DailyMetrics.company_id==company_id, models.DailyMetrics.trade_date_id==tradedate_id)).first().id
        fund_exits = session.query(models.Fundamentals).filter(models.Fundamentals.daily_metrics_id==daily_metrics_id).first() is not None
        if not fund_exits:
            new_fund = models.Fundamentals(daily_metrics_id = daily_metrics_id,
                                    open_price = d["open_price"],
                                    high_price = d["high_price"],
                                    close_price = d["close_price"],
                                    low_price = d["low_price"],
                                    volume = d["volume"],
                                    )
            session.add(new_fund)
            session.commit()

    def run(self, ag):
        fetch = YFinanceFetcher()
        if ag.date == None:
            utc_dt = datetime.now(timezone.utc)
            if utc_dt.hour + (utc_dt.minute/60) < close_utc_hour + 0.1: # market not closed yet
                date = utc_dt.date() - datetime.timedelta(days=1)
            else:
                date = utc_dt.date()
        else:
            date = ag.date
        date = date.strftime("%Y-%m-%d")
        if ag.ticker == None:
            ticker = "GOOGL"
        else:
            ticker = ag.ticker
        d = fetch.fetch_by_date(ticker, date)
        print(d)
        if ag.update_database:
            self.update_database(ticker, date, d)
