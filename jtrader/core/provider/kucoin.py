from __future__ import annotations

import asyncio
import os
from datetime import datetime
from kucoin.asyncio import KucoinSocketManager
from typing import Optional

from kucoin.client import Client

from jtrader.core.provider import Provider


class KuCoin(Provider):
    def __init__(self, is_sandbox: bool, no_notifications: Optional[bool] = False):
        super().__init__(is_sandbox, no_notifications)

        self.client_prop = Client(
            os.environ.get('KUCOIN_API_TOKEN'),
            os.environ.get('KUCOIN_API_SECRET'),
            os.environ.get('KUCOIN_API_PASSPHRASE'),
            is_sandbox
        )

    async def register_websockets(
            self,
            loop: asyncio.AbstractEventLoop,
            ticker: str,
            on_websocket_message: callable
    ) -> None:
        ksm = await KucoinSocketManager.create(loop, self.client, on_websocket_message)

        await ksm.subscribe(f"/market/candles:{ticker}_1min")

        while True:
            await asyncio.sleep(20, loop=loop)

    def chart(self, stock: str, start: datetime, end: datetime | None) -> dict | list:
        return self.client.get_kline_data(
            stock,
            start=start.microsecond,
            end=end,
            kline_type="1min"
        )

    def symbols(self) -> dict:
        return super().symbols()

    def intraday(self, stock: str) -> dict:
        return super().intraday(stock)
