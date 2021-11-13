from datetime import datetime, timedelta

import pandas as pd
from cement.core.log import LogInterface

from jtrader.core.indicator import __INDICATOR_MAP__
from jtrader.core.indicator.chain import Chain
from jtrader.core.indicator.indicator import Indicator
from jtrader.core.provider.kucoin import KuCoin as KuCoinProvider


class KuCoin:
    KLINE_COLUMNS = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']

    def __init__(self, provider: KuCoinProvider, ticker: str, logger: LogInterface):
        self.provider = provider
        self.has_initial_dataset = False
        self.ticker = ticker
        self.frames = None
        self.logger = logger

    async def on_websocket_message(self, message):
        def get_previous_dataset(dataset_start_time: str) -> list:
            date = datetime.fromtimestamp(int(dataset_start_time))

            start = date - timedelta(days=1)

            return self.provider.client.get_kline_data(
                self.ticker,
                start=start.microsecond,
                kline_type="1min"
            )

        def handle_candles_add(candle_data):
            self.logger.info('candle added...')
            candles = candle_data['data']['candles']
            start_time = candles[0]

            if self.frames is None:
                self.logger.info('looking up previous data...')
                previous = get_previous_dataset(start_time)

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

            chain = Chain(self.ticker, __INDICATOR_MAP__['all'])

            for validator in chain.get_validation_chain(True):
                is_valid = validator.is_valid(self.frames)

                if is_valid is not None:
                    if is_valid == Indicator.BULLISH:
                        self.logger.info(validator.get_name() + ': BULLISH')
                    elif is_valid == Indicator.BEARISH:
                        self.logger.warning(validator.get_name() + ': BEARISH')

        if 'subject' in message:
            if message['subject'] == 'trade.candles.add':
                handle_candles_add(message)
        else:
            self.logger.info(message)

    def subscribe(self) -> None:
        self.provider.connect_websocket(self.ticker, self.on_websocket_message)
