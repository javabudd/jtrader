import json
import random
from typing import Optional

import requests
import websocket
from cement.core.log import LogInterface

from jtrader.core.provider.provider import Provider


class KuCoin(Provider):
    BASE_URL = 'https://api.kucoin.com/api'

    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            version: Optional[str] = 'v1',
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, logger, no_notifications)

        self.client_prop = requests
        self.url = f"{self.BASE_URL}/{version}"

    @staticmethod
    def on_websocket_error(socket: websocket.WebSocketApp, error):
        print('### error ###')
        print('Error: ', error)

    @staticmethod
    def on_websocket_close(socket: websocket.WebSocketApp, close_status_code, close_msg):
        print('### closed ###')
        print('Code: ', close_status_code)
        print('Message: ', close_msg)

    def chart(self, stock: str, timeframe: str) -> dict:
        return self.client.stocks.chart(stock, timeframe=timeframe)

    def symbols(self) -> dict:
        return self.client.refdata.iexSymbols()

    def connect_websocket(
            self,
            on_websocket_open: callable,
            on_websocket_message: callable,
    ) -> None:
        response = self.client.post(self.url + '/bullet-public')
        response_data = json.loads(response.text)

        token = response_data['data']['token']
        connect_id = random.randrange(10000, 9000000)
        endpoint = response_data['data']['instanceServers'][0]['endpoint']

        if self.is_sandbox:
            websocket.enableTrace(True)

        ws = websocket.WebSocketApp(
            f"{endpoint}?token={token}&[connectId={connect_id}]",
            on_open=on_websocket_open,
            on_message=on_websocket_message,
            on_error=self.on_websocket_error,
            on_close=self.on_websocket_close
        )

        ws.run_forever(ping_interval=30, ping_timeout=10)
