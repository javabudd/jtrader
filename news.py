from sseclient import SSEClient

import utils
from secrets import IEX_CLOUD_API_TOKEN

stream_url = f'https://cloud-sse.iexapis.com/stable/news-stream?token={IEX_CLOUD_API_TOKEN}&symbols=spy'

messages = SSEClient(stream_url)
for msg in messages:
    utils.send_slack_message(msg.dump())
