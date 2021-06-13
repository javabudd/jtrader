from typing import Optional, List

import numpy as np
import pandas as pd
from zipline import run_algorithm
from zipline.api import order, order_target, record, symbol
from zipline.protocol import BarData

from jtrader.core.validator import __VALIDATION_MAP__


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

    def handle_data(self, context, data: BarData):
        context.i += 1
        if context.i < self.bar_count:
            return

        stock = context.asset

        if not data.can_trade(stock):
            return

        high = data.history(stock, 'high', bar_count=self.bar_count, frequency=self.frequency)
        low = data.history(stock, 'low', bar_count=self.bar_count, frequency=self.frequency)
        close = data.history(stock, 'close', bar_count=self.bar_count, frequency=self.frequency)
        volume = data.history(stock, 'volume', bar_count=self.bar_count, frequency=self.frequency)
        data_frame = pd.DataFrame({"high": high, "low": low, "close": close, "volume": volume})

        record(asset=data.current(stock, 'close'))

        if self.stock_qualifies_bullish(context, data.current(stock, 'price'), data_frame):
            order(stock, self.ORDER_AMOUNT)
        elif self.stock_qualifies_bearish(stock, data_frame):
            order_target(stock, 0)

    def initialize(self, context):
        context.i = 0
        context.asset = symbol(self.ticker)

    def run(self):
        run_algorithm(
            capital_base=self.CAPITAL_BASE,
            data_frequency=self.DATA_FREQUENCY,
            initialize=self.initialize,
            handle_data=self.handle_data,
            bundle=self.DATA_BUNDLE,
            start=self.start_date,
            end=self.end_date
        ).to_csv('out.csv')

    @staticmethod
    def get_validator(validator_name: str, ticker: str, is_bullish: bool):
        if validator_name in __VALIDATION_MAP__:
            return __VALIDATION_MAP__[validator_name](ticker, is_bullish=is_bullish)

        raise Exception

    def stock_qualifies_bullish(self, context, price, data_frame: pd.DataFrame):
        cash_left = context.portfolio.cash
        stock = context.asset

        if price * self.ORDER_AMOUNT > cash_left:
            return False

        for validator in self.buy_indicators:
            validator = self.get_validator(validator, stock, True)

            if not validator.is_valid(data_frame):
                return False

        return True

    def stock_qualifies_bearish(self, stock: str, data_frame: pd.DataFrame):
        for validator in self.sell_indicators:
            validator = self.get_validator(validator, stock, False)

            if not validator.is_valid(data_frame):
                return False

        return True
