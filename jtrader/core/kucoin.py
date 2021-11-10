import json
import random

import pandas as pd
import websocket

from jtrader.core.indicator.linear_regression import LinearRegression
from jtrader.core.indicator.macd import MACD
from jtrader.core.indicator.rsi import RSI
from jtrader.core.provider.kucoin import KuCoin as KuCoinProvider


class KuCoin:
    KLINE_COLUMNS = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']

    def __init__(self, provider: KuCoinProvider, ticker: str):
        self.provider = provider
        self.has_initial_dataset = False
        self.ticker = ticker

    def subscribe(self) -> None:
        self.provider.connect_websocket(self.on_websocket_open, self.on_websocket_message)

    def on_websocket_message(self, socket: websocket.WebSocketApp, message):
        def handle_candles_add(candle_data):
            print('candle added...')
            candles = candle_data['data']['candles']
            start_time = candles[0]
            previous_frames = pd.DataFrame(None, None, self.KLINE_COLUMNS)

            if not self.has_initial_dataset:
                print('looking up previous data...')
                previous = self.get_previous_dataset(start_time)
                if start_time != previous[0][0]:
                    previous.insert(0, candles)

                previous_frames = pd.concat([pd.DataFrame(previous, columns=self.KLINE_COLUMNS)], ignore_index=True)
                self.has_initial_dataset = True

            macd = MACD(self.ticker)
            rsi = RSI(self.ticker)
            lr = LinearRegression(self.ticker)

            print('MACD Signal: ', macd.is_valid(previous_frames))
            print('RSI Signal: ', rsi.is_valid(previous_frames))
            print('LR Signal: ', lr.is_valid(previous_frames))

        try:
            data = json.loads(message)
        except Exception:
            return

        if 'subject' in data:
            if data['subject'] == 'trade.candles.add':
                handle_candles_add(data)
        else:
            print(data)

    def on_websocket_open(self, socket: websocket.WebSocketApp):
        data = {
            "id": random.randrange(10000, 9000000),
            "type": "subscribe",
            "topic": f"/market/candles:{self.ticker}_1min",
            "privateChannel": False
        }

        socket.send(json.dumps(data))

    def get_previous_dataset(self, dataset_start_time: str) -> list:
        rest_response = self.provider.client.get(
            self.provider.url + f"/market/candles?type=1min&symbol={self.ticker}&startsAt={dataset_start_time}"
        )

        try:
            rest_response_data = json.loads(rest_response.text)
        except Exception:
            return []

        return rest_response_data['data']
