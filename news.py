import json

from sseclient import SSEClient

import utils
from secrets import IEX_CLOUD_API_TOKEN

stream_url = f'https://cloud-sse.iexapis.com/stable/news-stream?token={IEX_CLOUD_API_TOKEN}&symbols=yolo'

stream_messages = SSEClient(stream_url)
for messages in stream_messages:
    for message in json.loads(messages.data):
        if message['lang'] == 'et':
            utils.send_slack_message(message['headline'] + "\n" + message['url'], '#stock-news')
