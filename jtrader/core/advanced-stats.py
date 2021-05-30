import json

import requests

import utils
from jtrader.core.secrets import IEX_CLOUD_API_TOKEN

api_url = f'https://cloud.iexapis.com/stable/stock/AMC/advanced-stats?token={IEX_CLOUD_API_TOKEN}'
response = requests.get(api_url)
data = response.json()

utils.send_slack_message(json.dumps(data))
