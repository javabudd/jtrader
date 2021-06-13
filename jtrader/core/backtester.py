from typing import Optional

import pandas as pd
from zipline import run_algorithm
from zipline.api import order_target, record, symbol
from zipline.protocol import BarData

from jtrader.core.validator.rsi import RSIValidator
from jtrader.core.validator.volume import VolumeValidator


class Backtester:
    CAPITAL_BASE = 1000000
    ORDER_AMOUNT = 5000
    DATA_FREQUENCY = 'daily'
    DATA_BUNDLE = 'iex'

    def __init__(
            self,
            logger,
            ticker: str,
            start_date: str,
            end_date: str,
            frequency: Optional[str] = '1d',
            bar_count: Optional[int] = 45
    ):
        self.logger = logger
        self.ticker = ticker
        self.frequency = frequency
        self.bar_count = bar_count
        self.start_date = pd.to_datetime(start_date, utc=True)
        self.end_date = pd.to_datetime(end_date, utc=True)

    def handle_data(self, context, data: BarData):
        context.i += 1
        if context.i < self.bar_count:
            return

        high = data.history(context.asset, 'high', bar_count=self.bar_count, frequency=self.frequency)
        low = data.history(context.asset, 'low', bar_count=self.bar_count, frequency=self.frequency)
        close = data.history(context.asset, 'close', bar_count=self.bar_count, frequency=self.frequency)
        volume = data.history(context.asset, 'volume', bar_count=self.bar_count, frequency=self.frequency)

        # Currently only using an RSI buy and RSI+Volume sell strategy
        # @TODO grab strategies dynamically through command args
        rsi_validator = RSIValidator(context.asset)
        volume_validator = VolumeValidator(context.asset)
        data_frame = pd.DataFrame({"high": high, "low": low, "close": close, "volume": volume})

        if rsi_validator.is_valid(data_frame):
            order_target(context.asset, self.ORDER_AMOUNT)
        else:
            volume_validator.is_bullish = False
            rsi_validator.is_bullish = False
            if rsi_validator.is_valid(data_frame) and volume_validator.is_valid(data_frame):
                order_target(context.asset, 0)

        record(Asset=data.current(context.asset, 'close'))

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
