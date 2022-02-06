from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from typing import Optional

import requests
import websocket

from jtrader.core.provider import Provider


class LoopRing(Provider):
    BASE_URL = 'https://api3.loopring.io'

    def __init__(self, is_sandbox: bool, no_notifications: Optional[bool] = False):
        super().__init__(is_sandbox, no_notifications)

        self.client_prop = requests

    async def register_websockets(
            self,
            loop: asyncio.AbstractEventLoop,
            ticker: str,
            on_websocket_message: callable
    ) -> None:
        def _on_websocket_open(websocket_connection):
            websocket_connection.send(json.dumps({
                "op": "sub",
                "unsubscribeAll": True,
                "topics": [
                    {
                        "topic": "candlestick",
                        "market": ticker,
                        "interval": "1min"
                    }
                ]
            }))

        def _on_websocket_error(websocket_connection, error):
            print(error)

        def _on_websocket_close(websocket_connection, close_status_code, close_msg):
            print(close_status_code, close_msg)

            self.logger.info('Websocket connection closing...')

        response = self.client.get(f"{self.BASE_URL}/v3/ws/key")
        api_key = json.loads(response.text)['key']

        ws = websocket.WebSocketApp(
            f'wss://ws.api3.loopring.io/v3/ws?wsApiKey={api_key}',
            on_open=_on_websocket_open,
            on_message=on_websocket_message,
            on_error=_on_websocket_error,
            on_close=_on_websocket_close
        )

        ws.run_forever()

    def chart(self, stock: str, start: datetime, end: datetime | None) -> dict:
        start = int(time.mktime(start.timetuple()) * 1000)
        end = int(time.mktime(end.timetuple()) * 1000) if end is not None else int(
            time.mktime(datetime.now().timetuple()) * 1000)

        response = self.client.get(
            f"{self.BASE_URL}/api/v3/candlestick?market={stock}&interval=1min&start={start}&end={end}&limit=1440"
        )

        candles = json.loads(response.text)['candlesticks']

        data = {}
        for candle in candles:
            data.update(
                {
                    candles.index(candle): {
                        'date': candle[0],
                        'open': candle[1],
                        'close': candle[2],
                        'high': candle[3],
                        'low': candle[4],
                        'volume': candle[6],
                        'amount': candle[2]
                    }
                }
            )

        return data

    def symbols(self) -> dict:
        return super().symbols()

    def intraday(self, stock: str) -> dict:
        return super().intraday(stock)
