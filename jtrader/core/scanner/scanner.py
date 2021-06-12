import json
import math
import time
from datetime import datetime
from threading import Thread
from typing import Optional, List

import pandas as pd
from cement.core.log import LogInterface
from cement.utils.shell import spawn_thread
from dateutil.relativedelta import relativedelta
from pyEX import PyEXception

from jtrader import __STOCK_CSVS__
from jtrader.core.db import DB
from jtrader.core.iex import IEX
from jtrader.core.validator import __VALIDATION_MAP__
from jtrader.core.validator.chain import ChainValidator
from jtrader.core.validator.validator import Validator


class Scanner(IEX):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            indicators: Optional[Validator],
            stocks: Optional[str] = None,
            time_range: Optional[str] = None,
            as_intraday: Optional[bool] = True,
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, logger, no_notifications=no_notifications)

        self.time_range = time_range
        self.as_intraday = as_intraday
        self.db = DB()

        if stocks is None:
            self.stock_list = __STOCK_CSVS__['sp500']
        else:
            if stocks not in __STOCK_CSVS__:
                raise RuntimeError

            self.stock_list = __STOCK_CSVS__[stocks]

        self.indicators = []
        if indicators is None:
            self.indicators = __VALIDATION_MAP__['all']
        else:
            indicators = map(lambda x: x[0], indicators)
            for indicator in indicators:
                if indicator in __VALIDATION_MAP__ and indicator:
                    self.indicators.append(__VALIDATION_MAP__[indicator])

            if len(self.indicators) == 0:
                raise RuntimeError

    def run(self):
        start = datetime.now()

        self.send_notification(f"*Scanner started at {start.strftime('%Y-%m-%d %H:%M:%S')}*")

        num_lines = len(open(self.stock_list).readlines())
        chunk_size = math.floor(num_lines / 25)
        if self.is_sandbox:
            chunk_size = math.floor(num_lines / 2)

        stocks = pd.read_csv(self.stock_list, chunksize=chunk_size)

        if self.as_intraday:
            self.process_intraday(stocks)
        else:
            self.process(stocks)

        end = datetime.now()
        self.logger.info('Processing finished')
        self.send_notification(f"*Scanner finished at {end.strftime('%Y-%m-%d %H:%M:%S')}*")

    def process(self, stocks):
        today = datetime.today()
        columns = [
            'ticker',
            'date',
            'close',
            'high',
            'low',
            'open',
            'volume',
            'updated',
            'changeOverTime',
            'marketChangeOverTime',
            'uOpen',
            'uClose',
            'uHigh',
            'uLow',
            'uVolume',
            'fOpen',
            'fClose',
            'fHigh',
            'fLow',
            'fVolume',
            'change',
            'changePercent'
        ]

        delta = 60
        start = today + relativedelta(days=-delta)
        for chunk in enumerate(stocks):
            for stock in chunk[1]['Ticker']:
                results = self.db.get_historical_stock_range(
                    stock,
                    start,
                    today
                ).all()

                if len(results) == 0:
                    try:
                        historical = self.iex_client.stocks.chart(stock, timeframe="1y")
                    except PyEXception:
                        continue

                    stocks = []
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

                        stocks.append(stock_day)

                    session = self.db.create_session()
                    session.bulk_save_objects(stocks)
                    session.commit()

                data = pd.DataFrame(
                    self.db.get_historical_stock_range(
                        stock,
                        start,
                        today
                    ).all()
                )

                if data.empty:
                    self.logger.debug(f"Retrieved empty data set for stock {stock}")

                    continue

                data.columns = columns
                self.init_indicators(stock, data)

    def process_intraday(self, stocks):
        i = 1
        threads: List[Thread] = []
        for chunk in enumerate(stocks):
            thread_name = f"Thread-{i}"
            """ @thread """
            thread = spawn_thread(self.loop, True, False, args=(thread_name, chunk), daemon=True)
            threads.append(thread)
            i += 1

        while len(threads) > 0:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
                thread.join(1)

    def loop(self, thread_name, chunk):
        sleep = .2

        if self.is_sandbox:
            sleep = 2

        for ticker in chunk[1]['Ticker']:
            time.sleep(sleep)
            self.logger.info(f"({thread_name}) Processing ticker: {ticker}")
            self.init_indicators(ticker)

        return True

    def init_indicators(self, ticker, data=None):
        period = 'swing'
        if self.as_intraday:
            period = 'intraday'

        if len(self.indicators) > 1:
            self.indicators = [ChainValidator(ticker, self.indicators, logger=self.logger, iex_client=self.iex_client)]

        for indicator_class in self.indicators:
            indicator = indicator_class
            if not isinstance(indicator, ChainValidator):
                indicator = indicator(ticker, logger=self.logger, iex_client=self.iex_client)

            passed_validators = {}
            try:
                is_valid = indicator.is_valid(data)

                if is_valid is False:
                    continue

                if isinstance(indicator, ChainValidator):
                    chain = indicator.get_validation_chain()
                    has_valid_chain = True
                    passed_validators[indicator.get_name()] = []
                    chain_index = 0
                    for validator_chain in chain:
                        args = {}
                        if self.time_range is not None:
                            args["time_range"] = self.time_range

                        validator_chain = validator_chain(ticker, self.logger, self.iex_client, **args)
                        if validator_chain.is_valid(data) is False:
                            has_valid_chain = False
                            break  # break out of validation chain

                        passed_validators[indicator.get_name()].append(validator_chain.get_name())
                        chain_index += 1
                    if has_valid_chain is False:
                        continue  # continue to the next validator in list
                else:
                    passed_validators = [indicator.get_name()]

            except PyEXception as e:
                self.logger.error(e.args[0] + ' ' + e.args[1])

                break

            if len(passed_validators) > 0:
                message = {
                    "ticker": ticker,
                    "signal_type": "bullish",
                    "signal_period": period,
                    "indicators_triggered": passed_validators
                }

                message_string = json.dumps(message)

                self.logger.info(message_string)
                self.send_notification('```' + message_string + '```')
