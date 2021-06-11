from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import String


class DB:
    Base = declarative_base()

    def __init__(self, create_db: bool = False):
        engine = create_engine('sqlite:///stocks.db', echo=False)

        if create_db:
            DB.Base.metadata.create_all(engine)

        self.engine = engine
        self.result_cache = {}

    def create_session(self):
        session_maker = sessionmaker(bind=self.engine)

        return session_maker()

    def has_historical_stock_day(self, ticker: str, day: str):
        session_maker = sessionmaker(bind=self.engine)
        session = session_maker()

        ticker_filter = self.StockDay.ticker == ticker
        day_filter = self.StockDay.date == day

        has_stock_day = False
        for stock_day in session.query(self.StockDay).filter(ticker_filter).filter(day_filter):
            self.result_cache[ticker][day] = stock_day
            has_stock_day = True
            break

        return has_stock_day

    def get_historical_stock_day(self, ticker: str, day: str):
        if ticker in self.result_cache:
            if day in self.result_cache[ticker]:
                return self.result_cache[ticker]

        session_maker = sessionmaker(bind=self.engine)
        session = session_maker()

        ticker_filter = self.StockDay.ticker == ticker
        day_filter = self.StockDay.date == day

        stock = None
        for stock_day in session.query(self.StockDay).filter(ticker_filter).filter(day_filter):
            stock = stock_day

        if stock is not None:
            self.result_cache[ticker] = {}
            self.result_cache[ticker][day] = stock

        return stock

    def get_historical_stock_range(self, ticker: str, start_date: datetime, end_date: datetime):
        session_maker = sessionmaker(bind=self.engine)
        session = session_maker()

        ticker_filter = self.StockDay.ticker == ticker
        from_filter = self.StockDay.date >= start_date
        to_filter = self.StockDay.date <= end_date

        return session.query(self.StockDay).filter(ticker_filter).filter(from_filter).filter(to_filter)

    class StockDay(Base):
        __tablename__ = "stock_day"

        ticker = Column(String, primary_key=True)
        date = Column(Date, primary_key=True)
        close = Column(Float)
        high = Column(Float)
        low = Column(Float)
        open = Column(Float)
        volume = Column(Integer)
        updated_at = Column(Integer)
        change_over_time = Column(Integer)
        market_change_over_time = Column(Integer)
        u_open = Column(Float)
        u_close = Column(Float)
        u_high = Column(Float)
        u_low = Column(Float)
        u_volume = Column(Integer)
        f_open = Column(Float)
        f_close = Column(Float)
        f_high = Column(Float)
        f_low = Column(Float)
        f_volume = Column(Integer)
        change = Column(Integer)
        change_percent = Column(Integer)

        def __init__(
                self,
                ticker,
                date,
                close,
                high,
                low,
                s_open,
                volume,
                updated_at,
                change_over_time,
                market_change_over_time,
                u_open,
                u_close,
                u_high,
                u_low,
                u_volume,
                f_open,
                f_close,
                f_high,
                f_low,
                f_volume,
                change,
                change_percent
        ):
            self.ticker = ticker
            self.date = date
            self.close = close
            self.high = high
            self.low = low
            self.open = s_open
            self.volume = volume
            self.updated_at = updated_at
            self.change_over_time = change_over_time
            self.market_change_over_time = market_change_over_time
            self.u_open = u_open
            self.u_close = u_close
            self.u_high = u_high
            self.u_low = u_low
            self.u_volume = u_volume
            self.f_open = f_open
            self.f_close = f_close
            self.f_high = f_high
            self.f_low = f_low
            self.f_volume = f_volume
            self.change = change
            self.change_percent = change_percent

        def __iter__(self):
            yield self.ticker
            yield self.date
            yield self.close
            yield self.high
            yield self.low
            yield self.open
            yield self.volume
            yield self.updated_at
            yield self.change_over_time
            yield self.market_change_over_time
            yield self.u_open
            yield self.u_close
            yield self.u_high
            yield self.u_low
            yield self.u_volume
            yield self.f_open
            yield self.f_close
            yield self.f_high
            yield self.f_low
            yield self.f_volume
            yield self.change
            yield self.change_percent
