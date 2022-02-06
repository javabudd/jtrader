from jtrader.core.indicator import __INDICATOR_MAP__
from jtrader.core.indicator.chain import Chain
from jtrader.core.indicator.indicator import Indicator
from jtrader.core.trader import Trader


class LoopRing(Trader):
    def __init__(self, provider, ticker):
        super().__init__(provider, ticker)

    async def _on_websocket_message(self, message) -> None:
        if 'op' in message and message['op'] == 'sub':
            return

        item = {
            "date": message['topic']['data'][1],
            "open": message['topic']['data'][4],
            "close": message['topic']['data'][7],
            "high": message['topic']['data'][5],
            "low": message['topic']['data'][6],
            "volume": message['topic']['data'][3],
            "amount": message['topic']['data'][2],
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
