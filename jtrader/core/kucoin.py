import json
import random
from datetime import datetime, timedelta

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
        self.frames = None

    def subscribe(self) -> None:
        self.provider.connect_websocket(self.on_websocket_open, self.on_websocket_message)

    def on_websocket_message(self, socket: websocket.WebSocketApp, message):
        def handle_candles_add(candle_data):
            print('candle added...')
            candles = candle_data['data']['candles']
            start_time = candles[0]

            if self.frames is None:
                print('looking up previous data...')
                previous = self.get_previous_dataset(start_time)

                self.frames = pd.concat(
                    [pd.DataFrame(previous, columns=self.KLINE_COLUMNS)],
                    ignore_index=True
                )

            latest_item = self.frames.iloc[0]

            if start_time != latest_item['date']:
                item = {
                    "date": start_time,
                    "open": candles[1],
                    "close": candles[2],
                    "high": candles[3],
                    "low": candles[4],
                    "volume": candles[5],
                    "amount": candles[6]
                }
                self.frames = self.frames.append(item, ignore_index=True)
                self.frames.sort_values(by=['date'], inplace=True, ascending=False)
                self.frames.reset_index(inplace=True, drop=True)

            macd = MACD(self.ticker)
            rsi = RSI(self.ticker)
            lr = LinearRegression(self.ticker)

            print('MACD Signal:', macd.is_valid(self.frames))
            print('RSI Signal:', rsi.is_valid(self.frames))
            print('LR Signal:', lr.is_valid(self.frames))

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
        date = datetime.fromtimestamp(int(dataset_start_time))

        start = date - timedelta(days=1)

        rest_response = self.provider.client.get(
            self.provider.url + f"/market/candles?type=1min&symbol={self.ticker}&startsAt={start.microsecond}"
        )

        try:
            rest_response_data = json.loads(rest_response.text)
        except Exception:
            return []

        return rest_response_data['data']
