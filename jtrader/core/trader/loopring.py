from jtrader.core.trader import Trader


class LoopRing(Trader):
    def __init__(self, provider, ticker):
        super().__init__(provider, ticker)

    async def on_websocket_message(self, message) -> None:
        pass

    def subscribe_to_websocket(self) -> None:
        pass
