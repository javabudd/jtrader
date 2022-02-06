from abc import ABC, abstractmethod

from jtrader.core.provider import Provider


class Trader(ABC):
    def __init__(self, provider: Provider, ticker: str):
        self.provider = provider
        self.ticker = ticker

    @abstractmethod
    async def on_websocket_message(self, message) -> None:
        pass

    @abstractmethod
    def subscribe_to_websocket(self) -> None:
        pass

    def get_one_min_dataset(self):
        return self.provider.chart(self.ticker, '1m')
