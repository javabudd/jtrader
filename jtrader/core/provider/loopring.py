from __future__ import annotations

import asyncio
from datetime import datetime
from kucoin.asyncio import KucoinSocketManager

from jtrader.core.provider import Provider


class LoopRing(Provider):
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

    def chart(self, stock: str, start: datetime, end: datetime | None) -> dict:
        return self.client.GET('/api/v3/ticker')

    def symbols(self) -> dict:
        return super().symbols()

    def intraday(self, stock: str) -> dict:
        return super().intraday(stock)
