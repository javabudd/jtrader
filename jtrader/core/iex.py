from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
from typing import Optional

import requests
from sseclient import SSEClient

from jtrader.core.secrets import IEX_CLOUD_API_TOKEN, IEX_CLOUD_SANDBOX_API_TOKEN


class IEX(ABC):
    def __init__(self, is_sandbox: bool, version: Optional[str] = 'stable'):
        self.is_sandbox = is_sandbox
        self.version = version

    @abstractmethod
    def run(self):
        pass

    def send_iex_request(self, endpoint_path: str, query_params: Optional[dict] = None):
        api_url = self.get_api_url(endpoint_path, query_params)

        response = requests.get(api_url)

        try:
            data = response.json()
        except JSONDecodeError:
            data = {}

        return data

    def start_iex_stream(self, endpoint_path: str, query_params: Optional[dict] = None):
        version = self.version
        query_string = self.query_params_to_string(query_params)

        stream_url = \
            f'https://cloud-sse.iexapis.com/{version}/{endpoint_path}?token={IEX_CLOUD_API_TOKEN}{query_string}'

        return SSEClient(stream_url)

    def get_api_url(self, endpoint_path: str, query_params: Optional[dict] = None):
        mode = 'cloud'
        token = IEX_CLOUD_API_TOKEN

        if self.is_sandbox:
            token = IEX_CLOUD_SANDBOX_API_TOKEN
            mode = 'sandbox'

        version = self.version
        query_string = self.query_params_to_string(query_params)

        return f'https://{mode}.iexapis.com/{version}/{endpoint_path}?token={token}{query_string}'

    @staticmethod
    def query_params_to_string(query_params: Optional[dict] = None):
        query_string = ''
        if query_params is not None:
            for key in query_params.keys():
                value = query_params[key]
                query_string += f'&{key}={value}'

        return query_string
