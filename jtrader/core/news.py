import json

from sseclient import SSEClient

import jtrader.core.utils as utils
from jtrader.core.secrets import IEX_CLOUD_API_TOKEN


class News:
    def run(self):
        stream_url = f'https://cloud-sse.iexapis.com/stable/news-stream?token={IEX_CLOUD_API_TOKEN}&symbols=SPY'

        stream_messages = SSEClient(stream_url)
        for messages in stream_messages:
            for message in json.loads(messages.data):
                if message['lang'] == 'et':
                    utils.send_slack_message(message['headline'] + "\n" + message['url'], '#stock-news')
