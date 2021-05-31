import json

import jtrader.core.utils as utils
from jtrader.core.iex import IEX


class News(IEX):
    def run(self):
        stream_messages = self.start_iex_stream('news-stream', {"symbols": "SPY"})
        for messages in stream_messages:
            for message in json.loads(messages.data):
                if message['lang'] == 'et':
                    utils.send_slack_message(message['headline'] + "\n" + message['url'], '#stock-news')
