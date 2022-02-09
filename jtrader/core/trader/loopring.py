import json

from jtrader.core.trader import Trader


class LoopRing(Trader):
    def __init__(self, provider, ticker):
        super().__init__(provider, ticker)

    async def _on_websocket_message(self, ws, message) -> None:
        if message == 'ping':
            self.logger.debug('pong')
            ws.send('pong')
            return

        message = json.loads(message)
        if 'op' in message and message['op'] == 'sub':
            return

        self.logger.info('Received message: ' + str(message))

        item = {
            "date": message['data'][0],
            "open": message['data'][2],
            "close": message['data'][3],
            "high": message['data'][4],
            "low": message['data'][5],
            "volume": message['data'][7],
            "amount": message['data'][6],
        }

        self.frames = self.frames.append(item, ignore_index=True)
        self.frames.sort_values(by=['date'], inplace=True, ascending=False)
        self.frames.reset_index(inplace=True, drop=True)

        self._execute_chain_validation()
