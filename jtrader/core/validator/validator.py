from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from pyEX.client import Client


class Validator(ABC):
    def __init__(
            self,
            ticker: str,
            iex_client: Client,
            is_bullish: Optional[bool] = True,
            time_range: Optional[str] = '5d'
    ):
        self.iex_client = iex_client
        self.ticker = ticker
        self.is_bullish = is_bullish
        self.time_range = time_range

    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def get_validation_chain(self):
        pass

    @staticmethod
    def get_ema(period, values):
        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()
        a = np.convolve(values, weights, mode='full')[:len(values)]
        a[:period] = a[period]

        return a

    def get_time_range(self):
        return self.time_range

    def has_lower_low(self):
        historical_data = self.iex_client.stocks.chart(self.ticker, timeframe=self.time_range)
        quote_data = self.iex_client.stocks.quote(self.ticker)

        if not historical_data:
            return False

        lowest_low_historical = min(historical_data, key=lambda x: x["low"] is not None)

        if lowest_low_historical['low'] is None or quote_data['low'] is None:
            return False

        return quote_data['low'] < lowest_low_historical['low']
