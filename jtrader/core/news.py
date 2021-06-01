import json
import signal

import jtrader.core.utils as utils
from jtrader.core.iex import IEX


class News(IEX):
    def run(self):
        stream_messages = self.iex_client.streaming.newsSSE(
            "SPY",
            on_data=self.message_callback,
            exit=signal.CTRL_C_EVENT
        )
        for messages in stream_messages:
            for message in json.loads(messages.data):
                utils.send_slack_message(message['headline'] + "\n" + message['url'], '#stock-news')

    @staticmethod
    def message_callback(stream_messages):
        for message in stream_messages:
            utils.send_slack_message(message['headline'] + "\n" + message['url'], '#stock-news')
