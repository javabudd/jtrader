from jtrader.core.indicator import __INDICATOR_MAP__
from jtrader.core.indicator.chain import Chain
from jtrader.core.indicator.indicator import Indicator
from jtrader.core.trader import Trader


class KuCoin(Trader):
    async def _on_websocket_message(self, message) -> None:
        def handle_candles_add(candle_data):
            self.logger.info('candle added...')
            candles = candle_data['data']['candles']
            start_time = candles[0]
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

    def _subscribe_to_websocket(self) -> None:
        self.provider.connect_websocket(self.ticker, self._on_websocket_message)
