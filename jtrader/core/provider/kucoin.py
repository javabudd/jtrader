import asyncio
import os
from typing import Optional

from cement.core.log import LogInterface
from kucoin.asyncio import KucoinSocketManager
from kucoin.client import Client

from jtrader.core.provider.provider import Provider


class KuCoin(Provider):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, logger, no_notifications)

        self.client_prop = Client(
            os.environ.get('KUCOIN_API_TOKEN'),
            os.environ.get('KUCOIN_API_SECRET'),
            os.environ.get('KUCOIN_API_PASSPHRASE'),
            is_sandbox
        )

    def chart(self, stock: str, timeframe: str) -> dict:
        return self.client.stocks.chart(stock, timeframe=timeframe)

    def symbols(self) -> dict:
        return self.client.refdata.iexSymbols()

    async def main(self, loop, ticker: str, on_websocket_message: callable) -> None:
        ksm = await KucoinSocketManager.create(loop, self.client, on_websocket_message)

        await ksm.subscribe(f"/market/candles:{ticker}_1min")

        while True:
            await asyncio.sleep(20, loop=loop)

    def connect_websocket(self, ticker: str, on_websocket_message: callable) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main(loop, ticker, on_websocket_message))
