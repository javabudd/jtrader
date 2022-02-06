import json

from jtrader.core.trader import Trader


class LoopRing(Trader):
    def __init__(self, provider, ticker):
        super().__init__(provider, ticker)

    def _on_websocket_message(self, ws, message) -> None:
        self.logger.info('Received message: ' + str(message))

        if message == 'ping':
            ws.send('pong')

            return

        message = json.loads(message)
        if 'op' in message and message['op'] == 'sub':
            return

        item = {
            "date": message['topic']['data'][0],
            "open": message['topic']['data'][2],
            "close": message['topic']['data'][3],
            "high": message['topic']['data'][4],
            "low": message['topic']['data'][5],
            "volume": message['topic']['data'][7],
            "amount": message['topic']['data'][6],
        }

        self.frames = self.frames.append(item, ignore_index=True)
        self.frames.sort_values(by=['date'], inplace=True, ascending=False)
        self.frames.reset_index(inplace=True, drop=True)

        self._execute_chain_validation()
