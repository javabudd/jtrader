from abc import ABC, abstractmethod
from typing import Optional

from pyEX.client import Client


class Validator(ABC):
    def __init__(self, ticker: str, iex_client: Client, is_bullish: Optional[bool] = True):
        self.iex_client = iex_client
        self.ticker = ticker
        self.is_bullish = is_bullish

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def get_validation_chain(self):
        pass

    def has_lower_low(self, time_range: Optional[str] = '5d'):
        historical_data = self.iex_client.stocks.chart(self.ticker, timeframe=time_range)
        quote_data = self.iex_client.stocks.quote(self.ticker)

        if not historical_data:
            return False

        lowest_low_historical = min(historical_data, key=lambda x: x["low"])

        if lowest_low_historical['low'] is None or quote_data['low'] is None:
            return False

        return quote_data['low'] < lowest_low_historical['low']
