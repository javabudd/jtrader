from typing import Optional, List

import numpy as np
import pandas as pd

from jtrader.core.indicator import __INDICATOR_MAP__
from jtrader.core.indicator.indicator import Indicator


class Backtester:
    CAPITAL_BASE = 1000000
    ORDER_AMOUNT = 100
    DATA_FREQUENCY = 'daily'
    DATA_BUNDLE = 'iex'

    def __init__(
            self,
            logger,
            ticker: str,
            start_date: str,
            end_date: str,
            buy_indicators: List[str],
            sell_indicators: List[str],
            frequency: Optional[str] = '1d',
            bar_count: Optional[int] = 45
    ):
        self.logger = logger
        self.ticker = ticker
        self.buy_indicators = np.array(buy_indicators).flatten()
        self.sell_indicators = np.array(sell_indicators).flatten()
        self.frequency = frequency
        self.bar_count = bar_count
        self.start_date = pd.to_datetime(start_date, utc=True)
        self.end_date = pd.to_datetime(end_date, utc=True)

        self.cached_buy_indicators = {}
        self.cached_sell_indicators = {}

    @staticmethod
    def get_validator(validator_name: str, ticker: str):
        if validator_name in __INDICATOR_MAP__:
            return __INDICATOR_MAP__[validator_name](ticker)

        raise Exception

    def run(self):
        # @TODO implement a new backtester, zipline is too old :/
        pass

    def stock_qualifies_bullish(self, context, price, data_frame: pd.DataFrame):
        cash_left = context.portfolio.cash
        stock = context.asset

        if price * self.ORDER_AMOUNT > cash_left:
            return False

        for validator in self.buy_indicators:
            if validator in self.cached_buy_indicators:
                validator_instance = self.cached_buy_indicators[validator]
            else:
                validator_instance = self.get_validator(validator, stock)
                self.cached_buy_indicators[validator] = validator_instance

            if validator_instance.is_valid(data_frame) == Indicator.BULLISH:
                return True

        return False

    def stock_qualifies_bearish(self, stock: str, data_frame: pd.DataFrame):
        for validator in self.sell_indicators:
            if validator in self.cached_sell_indicators:
                validator_instance = self.cached_sell_indicators[validator]
            else:
                validator_instance = self.get_validator(validator, stock)
                self.cached_sell_indicators[validator] = validator_instance

            if validator_instance.is_valid(data_frame) == Indicator.BEARISH:
                return True

        return False
