from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from cement.core.log import LogInterface


class Indicator(ABC):
    WINDOW_SIZE_TEN = 10
    WINDOW_SIZE_FOURTEEN = 14
    WINDOW_SIZE_TWENTY = 20
    WINDOW_SIZE_TWENTY_EIGHT = 28
    WINDOW_SIZE_FORTY = 40
    WINDOW_SIZE_FIFTY_SEVEN = 57
    WINDOW_SIZE_EIGHTY = 80
    WINDOW_SIZE_ONE_HUNDRED_THIRTEEN = 113
    WINDOW_SIZE_ONE_HUNDRED_SIXTY = 160

    BULLISH = 0x0
    BEARISH = 0x1

    def __init__(self, ticker: str, logger: Optional[LogInterface] = None):
        self.logger_prop = logger
        self.ticker = ticker
        self.time_period = self.WINDOW_SIZE_TEN
        self.fast_period = self.WINDOW_SIZE_FOURTEEN
        self.slow_period = self.WINDOW_SIZE_TWENTY_EIGHT
        self.signal_period = self.WINDOW_SIZE_TEN

    @abstractmethod
    def is_valid(self, data, comparison_data=None):
        pass

    @staticmethod
    @abstractmethod
    def get_name():
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

        if historical_data['low'] is None or len(historical_data['low']) == 0:
            return False

        lowest_low_historical = min(historical_data['low'])

        return quote_data['low'] < lowest_low_historical

    @staticmethod
    def has_lower_high(data):
        historical_data = data.iloc[:-1]
        quote_data = data.iloc[-1]

        if historical_data['high'] is None or len(historical_data['high']) == 0:
            return False

        lowest_high_historical = min(historical_data['high'])

        return quote_data['high'] < lowest_high_historical

    @staticmethod
    def has_higher_low(data=None):
        historical_data = data.iloc[:-1]
        quote_data = data.iloc[-1]

        if historical_data['low'] is None or len(historical_data['low']) == 0:
            return False

        highest_low_historical = max(historical_data['low'])

        return quote_data['low'] > highest_low_historical

    @staticmethod
    def has_higher_high(data=None):
        historical_data = data.iloc[:-1]
        quote_data = data.iloc[-1]

        if historical_data['high'] is None or len(historical_data['high']) == 0:
            return False

        highest_high_historical = max(historical_data['high'])

        return quote_data['high'] > highest_high_historical

    def log_missing_close(self):
        self.logger.debug(f"{self.ticker} missing close data from provider")

    def log_missing_chart(self):
        self.logger.debug(f"{self.ticker} missing chart data from provider")

    def log_not_enough_data(self):
        self.logger.debug(f"{self.ticker} does not have enough data to process")

    def log_ema_fail(self, calculation):
        self.logger.debug(f"{self.ticker} Could not get EMA, setting to 0 ({calculation})")

    def log_error(self, exception_or_string):
        self.logger.error(f"{self.ticker} - {self.get_name()}: {exception_or_string}")

    def log_warning(self, exception_or_string):
        self.logger.warning(f"{self.ticker} - {self.get_name()}: {exception_or_string}")

    def log_invalid_chart_length(self):
        self.log_warning('Chart length invalid')
