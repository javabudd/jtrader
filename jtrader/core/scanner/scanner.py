import json
import time
from datetime import datetime
from threading import Thread
from typing import Optional, List

import numpy as np
import pandas as pd
from cement.core.log import LogInterface
from cement.utils.shell import spawn_thread
from dateutil.relativedelta import relativedelta
from pyEX import PyEXception

from jtrader import __STOCK_CSVS__
from jtrader.core.odm import ODM
from jtrader.core.provider.iex import IEX
from jtrader.core.utils.csv import get_stocks_chunked, CSV_COLUMNS
from jtrader.core.indicator import __INDICATOR_MAP__
from jtrader.core.indicator.chain import Chain
from jtrader.core.indicator.indicator import Indicator


class Scanner(IEX):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            indicators: Optional[List[Indicator]],
            stocks: Optional[str] = None,
            as_intraday: Optional[bool] = True,
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, logger, no_notifications=no_notifications)

        self.as_intraday = as_intraday
        self.odm = ODM()

        if stocks is None:
            self.stock_list = __STOCK_CSVS__['sp500']
        else:
            if stocks not in __STOCK_CSVS__:
                raise RuntimeError

            self.stock_list = __STOCK_CSVS__[stocks]

        self.indicators = []
        if indicators is None:
            self.indicators = __INDICATOR_MAP__['all']
        else:
            indicators = np.array(indicators).flatten()
            for indicator in indicators:
                if indicator in __INDICATOR_MAP__ and indicator:
                    self.indicators.append(__INDICATOR_MAP__[indicator])

            if len(self.indicators) == 0:
                raise RuntimeError

    @staticmethod
    def get_signal_string(is_valid):
        if is_valid == Indicator.BULLISH:
            signal_type = 'bullish'
        elif is_valid == Indicator.BEARISH:
            signal_type = 'bearish'
        else:
            raise ValueError

        return signal_type

    def run(self):
        start = datetime.now()

        self.send_notification(f"*Scanner started at {start.strftime('%Y-%m-%d %H:%M:%S')}*")

        stocks = get_stocks_chunked(self.stock_list, self.is_sandbox)

        if self.as_intraday:
            self.process_intraday(stocks)
        else:
            self.process_timeframe(stocks)

        end = datetime.now()
        self.logger.info('Processing finished')
        self.send_notification(f"*Scanner finished at {end.strftime('%Y-%m-%d %H:%M:%S')}*")

    def process_timeframe(self, stocks):
        today = datetime.today()
        delta = 365
        start = today + relativedelta(days=-delta)

        for chunk in enumerate(stocks):
            for stock in chunk[1]['Ticker']:
                data = pd.DataFrame(
                    self.odm.get_historical_stock_range(
                        stock,
                        start
                    )
                )

                if data.empty:
                    self.logger.debug(f"Retrieved empty data set for stock {stock}")

                    continue

                data.columns = CSV_COLUMNS
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
            if data is None:
                data = self.client.stocks.intradayDF(ticker, IEXOnly=True)

                if 'close' not in data:
                    self.logger.error(f"{ticker} Could not find closing intraday")

                    return False

        args = {"logger": self.logger}
        if len(self.indicators) > 1:
            self.indicators = [
                Chain(
                    ticker,
                    self.indicators,
                    **args
                )
            ]

        for indicator_class in self.indicators:
            indicator = indicator_class
            if not isinstance(indicator, Chain):
                indicator = indicator(ticker, **args)

            passed_validators = {}
            try:
                is_valid = indicator.is_valid(data)

                if is_valid is None:
                    continue

                signal_type = self.get_signal_string(is_valid)

                if isinstance(indicator, Chain):
                    chain = indicator.get_validation_chain()
                    has_valid_chain = True
                    passed_validators[indicator.get_name()] = []
                    chain_index = 0
                    for validator_chain in chain:
                        validator_chain = validator_chain(ticker, **args)
                        is_valid = validator_chain.is_valid(data)
                        if is_valid is None:
                            has_valid_chain = False
                            break  # break out of validation chain

                        signal_type = self.get_signal_string(is_valid)

                        passed_validators[indicator.get_name()].append(
                            {
                                "signal_type": signal_type,
                                "indicator": validator_chain.get_name()
                            }
                        )
                        chain_index += 1
                    if has_valid_chain is False:
                        continue  # continue to the next indicator in list
                else:
                    passed_validators = {"signal_type": signal_type, "indicator": indicator.get_name()}

            except PyEXception as e:
                self.logger.error(e.args[0] + ' ' + e.args[1])

                break

            if len(passed_validators) > 0:
                # test the theories

                # notify if successful
                message = {
                    "ticker": ticker,
                    "signal_period": period,
                    "indicators_triggered": passed_validators
                }

                message_string = json.dumps(message)

                self.logger.info(message_string)
                self.send_notification('```' + message_string + '```')
