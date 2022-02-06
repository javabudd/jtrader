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

        self._execute_chain_validation()
