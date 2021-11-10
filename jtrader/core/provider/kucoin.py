import json
import random
from typing import Optional

import pandas as pd
import requests
import websocket
from jtrader.core.indicator.macd import MACD
from cement.core.log import LogInterface

from jtrader.core.provider.provider import Provider


class KuCoin(Provider):
    BASE_URL = 'https://api.kucoin.com/api'

    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            ticker: str,
            version: Optional[str] = 'v1',
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, logger, no_notifications)

        self.client_prop = requests
        self.url = f"{self.BASE_URL}/{version}"
        self.ticker = ticker
        self.has_initial_dataset = False

    def chart(self, stock: str, timeframe: str) -> dict:
        return self.client.stocks.chart(stock, timeframe=timeframe)

    def symbols(self) -> dict:
        return self.client.refdata.iexSymbols()

    def connect_websocket(self) -> None:
        columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']

        def get_previous_dataset(start_time: str) -> list:
            rest_response = self.client.get(
                self.url + f"/market/candles?type=1min&symbol={self.ticker}&startsAt={start_time}"
            )

            try:
                rest_response_data = json.loads(rest_response.text)
            except Exception:
                return []

            return rest_response_data['data']

        def on_websocket_message(socket: websocket.WebSocketApp, message):
            print('### received ###')

            try:
                data = json.loads(message)
            except Exception:
                return

            if 'subject' in data:
                if data['subject'] == 'trade.candles.add':
                    candles = data['data']['candles']
                    start_time = candles[0]
                    previous_frames = pd.DataFrame(None, None, columns)

                    if not self.has_initial_dataset:
                        print('looking up previous data...')
                        previous = get_previous_dataset(start_time)
                        if start_time != previous[0][0]:
                            previous.insert(0, candles)

                        previous_frames = pd.concat([pd.DataFrame(previous, columns=columns)], ignore_index=True)
                        self.has_initial_dataset = True

                    macd = MACD(self.ticker)

                    print(macd.is_valid(previous_frames))
            else:
                print(data)

        def on_websocket_error(socket: websocket.WebSocketApp, error):
            print('### error ###')
            print('Error: ', error)

        def on_websocket_close(socket: websocket.WebSocketApp, close_status_code, close_msg):
            print('### closed ###')
            print('Code: ', close_status_code)
            print('Message: ', close_msg)

        def on_websocket_open(socket: websocket.WebSocketApp):
            data = {
                "id": random.randrange(10000, 9000000),
                "type": "subscribe",
                "topic": f"/market/candles:{self.ticker}_1min",
                "privateChannel": False
            }

            ws.send(json.dumps(data))

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
            on_error=on_websocket_error,
            on_close=on_websocket_close
        )

        ws.run_forever(ping_interval=30, ping_timeout=10)
