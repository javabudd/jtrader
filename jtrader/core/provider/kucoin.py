import json
import random
from typing import Optional

import requests
from cement.core.log import LogInterface
from websocket import WebSocketApp

from jtrader.core.provider.provider import Provider


class KuCoin(Provider):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            version: Optional[str] = 'v1',
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, logger, no_notifications)

        self.client_prop = requests
        self.url = f"https://api.kucoin.com/api/{version}/bullet-public"

    def chart(self, stock: str, timeframe: str) -> dict:
        return self.client.stocks.chart(stock, timeframe=timeframe)

    def symbols(self) -> dict:
        return self.client.refdata.iexSymbols()

    def connect_websocket(self) -> None:
        def on_websocket_message(socket: WebSocketApp, message):
            data = json.loads(message)

            if data['subject'] == 'trade.candles.add':
                print(data['data']['candles'])

        def on_websocket_error(socket: WebSocketApp, error):
            print(error)

        def on_websocket_close(socket: WebSocketApp, close_status_code, close_msg):
            print(socket.sock)

        def on_websocket_open(socket: WebSocketApp):
            data = {
                "id": random.randrange(10000, 9000000),
                "type": "subscribe",
                "topic": "/market/candles:LOKI-BTC_1min",
                "privateChannel": False,
                "response": True
            }

            ws.send(json.dumps(data))

        response = requests.post(self.url)
        response_data = json.loads(response.text)

        token = response_data['data']['token']
        connect_id = random.randrange(10000, 9000000)
        endpoint = response_data['data']['instanceServers'][0]['endpoint']

        ws = WebSocketApp(
            f"{endpoint}?token={token}&[connectId={connect_id}]",
            on_open=on_websocket_open,
            on_message=on_websocket_message,
            on_error=on_websocket_error,
            on_close=on_websocket_close
        )

        ws.run_forever()
