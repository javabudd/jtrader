from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import pandas as pd
from cement.core.log import LogInterface
from pyEX.client import Client


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

    def __init__(
            self,
            ticker: str,
            logger: Optional[LogInterface] = None,
            iex_client: Optional[Client] = None,
            is_bullish: Optional[bool] = True,
            time_range: Optional[str] = '5d',
            iex_only: Optional[bool] = True
    ):
        self.iex_client_prop = iex_client
        self.logger_prop = logger
        self.ticker = ticker
        self.is_bullish = is_bullish
        self.time_range = time_range
        self.iex_only = iex_only

    @abstractmethod
    def is_valid(self, data=None, comparison_data=None):
        pass

    @staticmethod
    def clean_dataframe(dataframe):
        dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)
        dataframe.dropna(inplace=True)

        return dataframe

    @property
    def iex_client(self):
        if self.iex_client_prop is None:
            raise RuntimeError

        return self.iex_client_prop

    @property
    def logger(self):
        if self.logger_prop is None:
            raise RuntimeError

        return self.logger_prop

    def get_time_range(self):
        return self.time_range

    def has_lower_low(self, data=None):
        if data is None:
            historical_data = pd.DataFrame(self.iex_client.stocks.chart(self.ticker, timeframe=self.time_range))
            quote_data = self.iex_client.stocks.quote(self.ticker)
        else:
            historical_data = data.iloc[:-1]
            quote_data = data.iloc[-1]

        lowest_low_historical = min(historical_data['low'])

        return quote_data['low'] < lowest_low_historical

    def has_lower_high(self, data=None):
        if data is None:
            historical_data = pd.DataFrame(self.iex_client.stocks.chart(self.ticker, timeframe=self.time_range))
            quote_data = self.iex_client.stocks.quote(self.ticker)
        else:
            historical_data = data.iloc[:-1]
            quote_data = data.iloc[-1]

        lowest_high_historical = min(historical_data['high'])

        return quote_data['high'] < lowest_high_historical

    def has_higher_low(self, data=None):
        if data is None:
            historical_data = pd.DataFrame(self.iex_client.stocks.chart(self.ticker, timeframe=self.time_range))
            quote_data = self.iex_client.stocks.quote(self.ticker)
        else:
            historical_data = data.iloc[:-1]
            quote_data = data.iloc[-1]

        highest_low_historical = max(historical_data['low'])

        return quote_data['low'] > highest_low_historical

    def has_higher_high(self, data=None):
        if data is None:
            historical_data = pd.DataFrame(self.iex_client.stocks.chart(self.ticker, timeframe=self.time_range))
            quote_data = self.iex_client.stocks.quote(self.ticker)
        else:
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
