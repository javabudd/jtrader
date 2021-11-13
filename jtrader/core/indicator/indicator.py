from abc import ABC, abstractmethod
from typing import Optional, Union, TypeVar

import numpy as np
from cement.core.log import LogInterface
from pandas import DataFrame


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

    BULLISH = TypeVar('BULLISH')
    BEARISH = TypeVar('BEARISH')

    def __init__(self, ticker: str, logger: Optional[LogInterface] = None):
        self.logger_prop = logger
        self.ticker = ticker
        self.time_period = self.WINDOW_SIZE_TEN
        self.fast_period = self.WINDOW_SIZE_FOURTEEN
        self.slow_period = self.WINDOW_SIZE_TWENTY_EIGHT
        self.signal_period = self.WINDOW_SIZE_TEN
        self._result_info = {}

    @abstractmethod
    def is_valid(self, data: DataFrame, comparison_data: DataFrame = None) -> Union[BULLISH, BEARISH, None]:
        pass

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        pass

    @property
    def result_info(self) -> dict:
        return self._result_info

    @staticmethod
    def clean_dataframe(dataframe: DataFrame) -> DataFrame:
        dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)
        dataframe.dropna(inplace=True)

        return dataframe

    @property
    def logger(self) -> LogInterface:
        if self.logger_prop is None:
            raise RuntimeError

        return self.logger_prop

    @staticmethod
    def has_lower_low(data: DataFrame) -> bool:
        historical_data = data.iloc[-2]
        quote_data = data.iloc[-1]

        if historical_data['low'] is None or len(historical_data['low']) == 0:
            return False

        lowest_low_historical = min(historical_data['low'])

        return quote_data['low'] < lowest_low_historical

    @staticmethod
    def has_lower_high(data: DataFrame) -> bool:
        historical_data = data.iloc[-2]
        quote_data = data.iloc[-1]

        if historical_data['high'] is None or len(historical_data['high']) == 0:
            return False

        lowest_high_historical = min(historical_data['high'])

        return quote_data['high'] < lowest_high_historical

    @staticmethod
    def has_higher_low(data: DataFrame = None) -> bool:
        historical_data = data.iloc[-2]
        quote_data = data.iloc[-1]

        if historical_data['low'] is None or len(historical_data['low']) == 0:
            return False

        highest_low_historical = max(historical_data['low'])

        return quote_data['low'] > highest_low_historical

    @staticmethod
    def has_higher_high(data: DataFrame = None) -> bool:
        historical_data = data.iloc[-2]
        quote_data = data.iloc[-1]

        if historical_data['high'] is None or len(historical_data['high']) == 0:
            return False

        highest_high_historical = max(historical_data['high'])

        return quote_data['high'] > highest_high_historical

    def log_missing_close(self) -> None:
        self.logger.debug(f"{self.ticker} missing close data from provider")

    def log_missing_chart(self) -> None:
        self.logger.debug(f"{self.ticker} missing chart data from provider")

    def log_not_enough_data(self) -> None:
        self.logger.debug(f"{self.ticker} does not have enough data to process")

    def log_ema_fail(self, calculation: str) -> None:
        self.logger.debug(f"{self.ticker} Could not get EMA, setting to 0 ({calculation})")

    def log_error(self, exception_or_string: Union[Exception, str]) -> None:
        self.logger.error(f"{self.ticker} - {self.get_name()}: {exception_or_string}")

    def log_warning(self, exception_or_string: Union[Exception, str]) -> None:
        self.logger.warning(f"{self.ticker} - {self.get_name()}: {exception_or_string}")

    def log_invalid_chart_length(self) -> None:
        self.log_warning('Chart length invalid')
