import time
from datetime import datetime
from threading import Thread
from typing import List

import pandas as pd
from cement.core.log import LogInterface
from cement.utils.shell import spawn_thread
from dateutil.relativedelta import relativedelta

from jtrader.core.db import DB
from jtrader.core.odm import ODM
from jtrader.core.provider.provider import Provider
from jtrader.core.utils.csv import get_stocks_chunked


class Worker:
    def __init__(self, provider: Provider, logger: LogInterface):
        self.provider = provider
        self.logger = logger
        self.odm = ODM()

    @staticmethod
    def timeframe_to_days(timeframe, as_stock_frame: bool = False) -> int:
        if timeframe.find('d') != -1:
            return int(timeframe.strip('d')) if as_stock_frame else int(timeframe.strip('d')) + 2

        if timeframe.find('y') != -1:
            year = timeframe.strip('y')

            return int(year) * 252 if as_stock_frame else int(year) * 365

        raise ValueError

    def run(self):
        while True:
            stock_list = 'all_stocks'

            self.logger.info(f"Processing stock list {stock_list}...")

            stocks = get_stocks_chunked(f"files/{stock_list}.csv", False, 50)

            i = 1
            threads: List[Thread] = []
            for chunk in enumerate(stocks):
                thread_name = f"Thread-{i}"
                """ @thread """
                thread = spawn_thread(self.insert_stocks, True, False, args=(thread_name, chunk), daemon=True)
                threads.append(thread)
                i += 1

            while len(threads) > 0:
                for thread in threads:
                    if not thread.is_alive():
                        threads.remove(thread)
                    thread.join(1)

            sleep_hours = 12
            sleep_time = 60 * 60 * sleep_hours

            self.logger.info(f"Sleeping for {sleep_hours} hours...")

            time.sleep(sleep_time)

    def insert_stocks(self, thread_id: str, chunk: pd.DataFrame, timeframe: str = '2y'):
        db = DB()
        today = datetime.today()
        days = self.timeframe_to_days(timeframe)
        start = today + relativedelta(days=-days)

        for stock in chunk[1]['Ticker']:
            self.logger.info(f"{thread_id} - Processing ticker {stock}...")

            odm_entry_length = len(self.odm.get_historical_stock_range(stock, start))

            provider_entries = db.get_historical_stock_range(stock, start, today).all()

            # try:
            #     provider_entries = self.provider.stocks.chart(stock, timeframe=timeframe)
            # except IEXClient.PyEXception:
            #     continue

            if odm_entry_length >= len(provider_entries):
                self.logger.warning(f"Skipping record insertion for {stock}...")

                continue

            self.logger.debug('odm count: ' + str(odm_entry_length))
            self.logger.debug('db count: ' + str(len(provider_entries)))

            with self.odm.table.batch_writer() as batch:
                for result in provider_entries:
                    if self.odm.get_historical_stock_day(stock, result.date) is not None:
                        continue

                    self.odm.put_item(batch, stock, result)

        return True
