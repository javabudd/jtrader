from datetime import datetime
from threading import Thread
from typing import List

import pandas as pd
from cement.core.log import LogInterface
from cement.utils.shell import spawn_thread
from dateutil.relativedelta import relativedelta
from pyEX import PyEXception

from jtrader import chunk_threaded
from jtrader.core.odm import ODM
from jtrader.core.provider.provider import Provider
from jtrader.core.utils.stock import timeframe_to_days


class Worker:
    def __init__(self, provider: Provider, logger: LogInterface):
        self.provider = provider
        self.logger = logger
        self.odm = ODM()

    def run(self):
        i = 1
        threads: List[Thread] = []
        for chunk in chunk_threaded(self.provider.symbols(), False, 25):
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

    def insert_stocks(self, thread_id: str, chunk: pd.DataFrame, timeframe: str = '5d'):
        today = datetime.today()
        days = timeframe_to_days(timeframe)
        start = today + relativedelta(days=-days)

        for stock in chunk:
            if stock['isEnabled'] is False:
                continue

            stock_symbol = stock['symbol']

            self.logger.info(f"{thread_id} - Processing ticker {stock_symbol}...")

            odm_entry_length = len(self.odm.get_historical_stock_range(stock_symbol, start))

            try:
                provider_entries = self.provider.chart(stock_symbol, timeframe=timeframe)
            except PyEXception:
                self.logger.warning(f"Failed retrieving provider data for {stock_symbol}...")

                continue

            if odm_entry_length >= len(provider_entries):
                self.logger.info(f"Skipping record insertion for {stock_symbol}...")

                continue

            self.logger.debug('odm count: ' + str(odm_entry_length))
            self.logger.debug('provider count: ' + str(len(provider_entries)))

            with self.odm.table.batch_writer() as batch:
                for result in provider_entries:
                    if self.odm.get_historical_stock_day(stock_symbol, result['date']) is not None:
                        continue

                    self.odm.put_item(batch, stock_symbol, result)

        return True
