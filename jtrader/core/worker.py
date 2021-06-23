import time
from datetime import datetime

import pandas as pd
import pyEX as IEXClient
from cement.core.log import LogInterface
from dateutil.relativedelta import relativedelta
from pyEX import PyEXception

from jtrader.core.db import DB


class Worker:
    def __init__(self, iex_client: IEXClient, logger: LogInterface):
        self.iex_client = iex_client
        self.logger = logger
        self.db = DB()

    def run(self):
        while True:
            stock_list = 'all_stocks'

            self.logger.info(f"Processing stock list {stock_list}...")

            stocks = pd.read_csv(f"files/{stock_list}.csv")

            self.insert_stocks(stocks)

            sleep_hours = 12
            sleep_time = 60 * 60 * sleep_hours

            self.logger.info(f"Sleeping for {sleep_hours} hours...")

            time.sleep(sleep_time)

    def insert_stocks(self, stocks: pd.DataFrame, timeframe: str = '2y'):
        days = self.timeframe_to_days(timeframe)
        today = datetime.today()
        start = today + relativedelta(days=-days)

        for stock in stocks['Ticker']:
            self.logger.info(f"Processing ticker {stock}...")

            entries_in_db = self.db.get_historical_stock_range(stock, start, today).count()

            if entries_in_db != 0 and self.timeframe_to_days(timeframe, True) / entries_in_db + - 2 <= 1:
                self.logger.warning(f"Skipping record insertion for {stock}...")

                continue

            try:
                historical = self.iex_client.stocks.chart(stock, timeframe=timeframe)
            except PyEXception:
                continue

            stocks_to_persist = []
            for result in historical:
                if self.db.get_historical_stock_day(stock, result['date']):
                    continue

                stock_day = self.db.StockDay(
                    stock,
                    datetime.strptime(result['date'], '%Y-%m-%d'),
                    result['close'],
                    result['high'],
                    result['low'],
                    result['open'],
                    result['volume'],
                    result['updated'] if 'updated' in result else None,
                    result['changeOverTime'],
                    result['marketChangeOverTime'],
                    result['uOpen'] if 'uOpen' in result else None,
                    result['uClose'] if 'uClose' in result else None,
                    result['uHigh'] if 'uHigh' in result else None,
                    result['uLow'] if 'uLow' in result else None,
                    result['uVolume'] if 'uVolume' in result else None,
                    result['fOpen'] if 'fOpen' in result else None,
                    result['fClose'] if 'fClose' in result else None,
                    result['fHigh'] if 'fHigh' in result else None,
                    result['fLow'] if 'fLow' in result else None,
                    result['fVolume'] if 'fVolume' in result else None,
                    result['change'],
                    result['changePercent']
                )

                stocks_to_persist.append(stock_day)

            session = self.db.create_session()
            session.bulk_save_objects(stocks_to_persist)
            session.commit()

    @staticmethod
    def timeframe_to_days(timeframe, as_stock_frame: bool = False) -> int:
        if timeframe.find('d') != -1:
            return int(timeframe.strip('d')) if as_stock_frame else int(timeframe.strip('d')) + 2

        if timeframe.find('y') != -1:
            year = timeframe.strip('y')

            return int(year) * 252 if as_stock_frame else int(year) * 365

        raise ValueError
