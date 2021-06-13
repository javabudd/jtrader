import time
from datetime import datetime

import pandas as pd
import pyEX as IEXClient
from cement.core.log import LogInterface
from pyEX import PyEXception

from jtrader.core.db import DB


class Worker:
    TEST = 1

    def __init__(self, iex_client: IEXClient, logger: LogInterface):
        self.iex_client = iex_client
        self.logger = logger
        self.db = DB()

    def run(self):
        while True:
            stock_list = 'sp_500_stocks'

            self.logger.info(f"Processing stock list {stock_list}...")

            stocks = pd.read_csv(f"files/{stock_list}.csv")

            self.insert_stocks(stocks)

            sleep_hours = 12
            sleep_time = 60 * 60 * sleep_hours

            self.logger.info(f"Sleeping for {sleep_hours} hours...")

            time.sleep(sleep_time)

    def insert_stocks(self, stocks: pd.DataFrame, timeframe: str = '5d'):
        for stock in stocks['Ticker']:
            try:
                historical = self.iex_client.stocks.chart(stock, timeframe=timeframe)
            except PyEXception:
                continue

            stocks_to_persist = []
            for result in historical:
                if self.db.get_historical_stock_day(stock, result['date']):
                    continue

                if 'uOpen' not in result:
                    self.logger.info(f"Could not get unadjusted close data for {stock}")

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
                    result['uOpen'],
                    result['uClose'],
                    result['uHigh'],
                    result['uLow'],
                    result['uVolume'],
                    result['fOpen'],
                    result['fClose'],
                    result['fHigh'],
                    result['fLow'],
                    result['fVolume'],
                    result['change'],
                    result['changePercent']
                )

                stocks_to_persist.append(stock_day)

            session = self.db.create_session()
            session.bulk_save_objects(stocks_to_persist)
            session.commit()
