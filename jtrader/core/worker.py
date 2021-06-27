import time
from datetime import datetime

import pandas as pd
import pyEX as IEXClient
from cement.core.log import LogInterface
from dateutil.relativedelta import relativedelta
from pyEX import PyEXception

from jtrader.core.odm import ODM


class Worker:
    def __init__(self, iex_client: IEXClient, logger: LogInterface):
        self.iex_client = iex_client
        self.logger = logger
        self.odm = ODM()

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
        start = datetime.today() + relativedelta(days=-days)

        for stock in stocks['Ticker']:
            self.logger.info(f"Processing ticker {stock}...")

            odm_entry_length = len(self.odm.get_historical_stock_range(stock, start))

            try:
                iex_entries = self.iex_client.stocks.chart(stock, timeframe=timeframe)
            except PyEXception:
                continue

            if odm_entry_length >= len(iex_entries):
                self.logger.warning(f"Skipping record insertion for {stock}...")

                continue

            self.logger.debug('odm count: ' + str(odm_entry_length))
            self.logger.debug('iex count: ' + str(len(iex_entries)))

            with self.odm.table.batch_writer() as batch:
                for result in iex_entries:
                    if self.odm.get_historical_stock_day(stock, result.date) is not None:
                        continue

                    self.odm.put_item(batch, stock, result)

    @staticmethod
    def timeframe_to_days(timeframe, as_stock_frame: bool = False) -> int:
        if timeframe.find('d') != -1:
            return int(timeframe.strip('d')) if as_stock_frame else int(timeframe.strip('d')) + 2

        if timeframe.find('y') != -1:
            year = timeframe.strip('y')

            return int(year) * 252 if as_stock_frame else int(year) * 365

        raise ValueError
