from typing import Optional

import requests

from jtrader.core.secrets import IEX_CLOUD_API_TOKEN


class IEX:
    def __init__(self, is_sandbox: bool, version: Optional[str] = 'stable'):
        self.is_sandbox = is_sandbox
        self.version = version

    def send_iex_request(self, endpoint_path: str, query_params: Optional[dict] = None):
        api_url = self.get_api_url(endpoint_path, query_params)

        response = requests.get(api_url)

        return response.json()

    def get_api_url(self, endpoint_path: str, query_params: Optional[dict] = None):
        mode = 'cloud'

        if self.is_sandbox:
            mode = 'sandbox'

        version = self.version

        query_string = ''
        if query_params is not None:
            for key in query_params.keys():
                value = query_params[key]
                query_string += f'&{key}={value}'

        return f'https://{mode}.iexapis.com/{version}/{endpoint_path}?token={IEX_CLOUD_API_TOKEN}{query_string}'
