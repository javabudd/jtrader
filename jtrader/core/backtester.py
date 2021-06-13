from typing import Optional

import pandas as pd
from zipline import run_algorithm
from zipline.api import order_target, record, symbol
from zipline.protocol import BarData

from jtrader.core.validator.rsi import RSIValidator
from jtrader.core.validator.volume import VolumeValidator


class Backtester:
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

        try:
            self.start_date = pd.to_datetime(start_date, utc=True)
        except TypeError as e:
            self.logger.error('Could not parse start date')

            raise e

        try:
            self.end_date = pd.to_datetime(end_date, utc=True)
        except TypeError as e:
            self.logger.error('Could not parse end date')

            raise e

    def handle_data(self, context, data: BarData):
        context.i += 1
        if context.i < self.bar_count:
            return

        high = data.history(context.asset, 'high', bar_count=self.bar_count, frequency=self.frequency)
        low = data.history(context.asset, 'low', bar_count=self.bar_count, frequency=self.frequency)
        close = data.history(context.asset, 'close', bar_count=self.bar_count, frequency=self.frequency)
        volume = data.history(context.asset, 'volume', bar_count=self.bar_count, frequency=self.frequency)

        rsi_validator = RSIValidator(context.asset)
        volume_validator = VolumeValidator(context.asset)
        data_frame = pd.DataFrame({"high": high, "low": low, "close": close, "volume": volume})

        if rsi_validator.is_valid(data_frame):
            order_target(context.asset, 5000)
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
            capital_base=1000000,
            data_frequency='daily',
            initialize=self.initialize,
            handle_data=self.handle_data,
            bundle='quandl',
            start=self.start_date,
            end=self.end_date
        ).to_csv('out.csv')
