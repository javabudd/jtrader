from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from cement.core.log import LogInterface


class Validator(ABC):
    WINDOW_SIZES = [
        10,
        14,
        20,
        28,
        40,
        57,
        80,
        113,
        160
    ]

    BULLISH = 0x0
    BEARISH = 0x1

    def __init__(self, ticker: str, logger: Optional[LogInterface] = None):
        self.logger_prop = logger
        self.ticker = ticker

    @abstractmethod
    def is_valid(self, data, comparison_data=None):
        pass

    @staticmethod
    def clean_dataframe(dataframe):
        dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)
        dataframe.dropna(inplace=True)

        return dataframe

    @property
    def logger(self):
        if self.logger_prop is None:
            raise RuntimeError

        return self.logger_prop

    @staticmethod
    def has_lower_low(data):
        historical_data = data.iloc[:-1]
        quote_data = data.iloc[-1]

        lowest_low_historical = min(historical_data['low'])

        return quote_data['low'] < lowest_low_historical

    @staticmethod
    def has_lower_high(data):
        historical_data = data.iloc[:-1]
        quote_data = data.iloc[-1]

        lowest_high_historical = min(historical_data['high'])

        return quote_data['high'] < lowest_high_historical

    @staticmethod
    def has_higher_low(data=None):
        historical_data = data.iloc[:-1]
        quote_data = data.iloc[-1]

        highest_low_historical = max(historical_data['low'])

        return quote_data['low'] > highest_low_historical

    @staticmethod
    def has_higher_high(data=None):
        historical_data = data.iloc[:-1]
        quote_data = data.iloc[-1]

        highest_high_historical = max(historical_data['high'])

        return quote_data['high'] > highest_high_historical

    def log_missing_close(self):
        self.logger.debug(f"{self.ticker} missing close data from IEX")

    def log_missing_chart(self):
        self.logger.debug(f"{self.ticker} missing chart data from IEX")

    def log_not_enough_chart_data(self):
        self.logger.debug(f"{self.ticker} has a chart length of one")

    def log_ema_fail(self, calculation):
        self.logger.debug(f"{self.ticker} Could not get EMA, setting to 0 ({calculation})")
