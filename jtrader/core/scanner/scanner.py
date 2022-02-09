import json
import time
from datetime import datetime
from threading import Thread
from typing import Optional, List

import numpy as np
import pandas as pd
from cement.utils.shell import spawn_thread
from dateutil.relativedelta import relativedelta
from pyEX import PyEXception

from jtrader import chunk_threaded
from jtrader.core.indicator import __INDICATOR_MAP__
from jtrader.core.indicator.chain import Chain
from jtrader.core.indicator.indicator import Indicator
from jtrader.core.odm import ODM
from jtrader.core.provider import IEX


class Scanner(IEX):
    def __init__(
            self,
            is_sandbox: bool,
            indicators: Optional[List[Indicator]],
            as_intraday: Optional[bool] = True,
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, no_notifications=no_notifications)

        self.as_intraday = as_intraday
        self.odm = ODM()
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
        stocks = self.client.symbols()

        if self.as_intraday:
            self.process_intraday(stocks)
        else:
            self.process_timeframe(stocks)

        self.logger.info('Processing finished')

    def process_timeframe(self, stocks):
        today = datetime.today()
        delta = 365
        start = today + relativedelta(days=-delta)

        for stock in stocks:
            data = pd.DataFrame(
                self.odm.get_historical_stock_range(
                    stock['symbol'],
                    start
                )
            )

            data = data.iloc[::-1].reset_index(drop=True)

            if data.empty:
                self.logger.debug(f"Retrieved empty data set for stock {stock['symbol']}")

                continue

            self.init_indicators(stock['symbol'], data)

    def process_intraday(self, stocks):
        i = 1
        threads: List[Thread] = []

        chunked = chunk_threaded(stocks, self.is_sandbox, 25)

        for chunk in chunked:
            thread_name = f"Thread-{i}"
            """ @thread """
            thread = spawn_thread(self.intraday_loop, True, False, args=(thread_name, chunk), daemon=True)
            threads.append(thread)
            i += 1

        while len(threads) > 0:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
                thread.join(1)

    def intraday_loop(self, thread_name, chunk):
        sleep = .2

        if self.is_sandbox:
            sleep = 2

        for stock in chunk:
            time.sleep(sleep)
            self.logger.info(f"({thread_name}) Processing ticker: {stock['symbol']}")
            self.init_indicators(stock['symbol'])

        return True

    def init_indicators(self, ticker: str, data=None):
        period = 'swing'
        if self.as_intraday and data is None:
            period = 'intraday'
            data = self.client.stocks.intradayDF(ticker, IEXOnly=True)
            if 'close' not in data:
                self.logger.error(f"{ticker} Could not find closing intraday")

                return False

        if len(self.indicators) > 1:
            self.indicators = [Chain(ticker, self.indicators)]

        for indicator_class in self.indicators:
            indicator = indicator_class
            if not isinstance(indicator, Chain):
                indicator = indicator(ticker)

            passed_validators = {}
            try:
                if isinstance(indicator, Chain):
                    chain = indicator.get_validation_chain()
                    has_valid_chain = True
                    passed_validators[indicator.get_name()] = []
                    chain_index = 0
                    previous_validation = None
                    for indicator_chain in chain:
                        indicator_chain = indicator_chain(ticker)
                        is_valid = indicator_chain.is_valid(data)

                        if is_valid is None or (
                                previous_validation == Indicator.BULLISH and is_valid == Indicator.BEARISH or
                                previous_validation == Indicator.BEARISH and is_valid == Indicator.BULLISH
                        ):
                            has_valid_chain = False
                            break  # break out of validation chain

                        previous_validation = is_valid

                        signal_type = self.get_signal_string(is_valid)

                        passed_validators[indicator.get_name()].append(
                            self.get_passed_validator_dict(signal_type, indicator_chain)
                        )
                        chain_index += 1
                    if has_valid_chain is False:
                        continue  # continue to the next indicator in list
                else:
                    is_valid = indicator.is_valid(data)

                    if is_valid is None:
                        continue

                    signal_type = self.get_signal_string(is_valid)

                    passed_validators = self.get_passed_validator_dict(signal_type, indicator)

            except PyEXception as e:
                self.logger.error(e.args[0] + ' ' + e.args[1])

                break

            if len(passed_validators) > 0:
                message = {
                    "ticker": ticker,
                    "signal_period": period,
                    "indicators_triggered": passed_validators
                }

                message_string = json.dumps(message)

                self.logger.info(message_string)
                self.send_notification('```' + message_string + '```')

    @staticmethod
    def get_passed_validator_dict(signal_type: str, indicator: Indicator) -> dict:
        return {
            "signal_type": signal_type,
            "indicator": indicator.get_name(),
            "extra": indicator.result_info
        }
