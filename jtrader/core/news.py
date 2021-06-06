import json

from jtrader.core.iex import IEX


class News(IEX):
    def run(self):
        stream_messages = self.iex_client.streaming.newsSSE(
            "SPY",
            on_data=self.message_callback
        )
        for messages in stream_messages:
            for message in json.loads(messages.data):
                self.send_notification(message['headline'] + "\n" + message['url'], '#stock-news')

    def message_callback(self, stream_messages):
        for message in stream_messages:
            self.send_notification(message['headline'] + "\n" + message['url'], '#stock-news')
