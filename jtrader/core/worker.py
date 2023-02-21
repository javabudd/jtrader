from datetime import datetime
from threading import Thread
from typing import List

import pandas as pd
from cement.core.log import LogInterface
from cement.utils.shell import spawn_thread
from pyEX import PyEXception

from jtrader import chunk_threaded
from jtrader.core.odm import ODM
from jtrader.core.provider import Provider


class Worker:
    def __init__(self, provider: Provider, logger: LogInterface):
        self.provider = provider
        self.logger = logger
        self.odm = ODM()

    def run(self):
        i = 1
        threads: List[Thread] = []
        symbols = self.provider.symbols()

        if len(symbols) > 5:
            for chunk in chunk_threaded(symbols, False, 5):
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
        else:
            df = pd.DataFrame(symbols)
            self.insert_stocks('Thread-1', df)

    def insert_stocks(self, thread_id: str, chunk: pd.DataFrame):
        today = datetime.today()

        for stock in chunk:
            if stock['isEnabled'] is False:
                continue

            stock_symbol = stock['symbol']

            self.logger.info(f"{thread_id} - Processing ticker {stock_symbol}...")

            last_day = self.odm.get_last_stock_day(stock_symbol)
            diff = today - last_day
            days = diff.days

            if days == 0:
                continue

            if days == 1:
                timeframe = '1d'
            elif days <= 5:
                timeframe = '5d'
            elif days <= 30:
                timeframe = '1m'
            elif days <= 90:
                timeframe = '3m'
            elif days <= 180:
                timeframe = '6m'
            elif days <= 365:
                timeframe = '1y'
            else:
                timeframe = 'max'

            try:
                provider_entries = self.provider.chart(stock_symbol, None, None, timeframe)
            except PyEXception:
                self.logger.warning(f"Failed retrieving provider data for {stock_symbol}...")

                continue

            with self.odm.stock_table.batch_writer(overwrite_by_pkeys=['ticker', 'date']) as batch:
                for result in provider_entries:
                    self.odm.put_stock(batch, stock_symbol, result)

        return True
