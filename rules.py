import requests
from secrets import IEX_CLOUD_API_TOKEN

api_url = f'https://cloud.iexapis.com/stable/rules/schema?token={IEX_CLOUD_API_TOKEN}'
response = requests.get(api_url)
data = response.json()

print(data)