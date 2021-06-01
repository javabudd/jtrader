from abc import ABC, abstractmethod
from typing import Optional

import pyEX as IEXClient
from cement.core.log import LogInterface

from jtrader.core.secrets import IEX_CLOUD_API_TOKEN, IEX_CLOUD_SANDBOX_API_TOKEN


class IEX(ABC):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            version: Optional[str] = 'stable'
    ):
        self.is_sandbox = is_sandbox
        self.logger = logger

        token = IEX_CLOUD_API_TOKEN
        if self.is_sandbox:
            version = 'sandbox'
            token = IEX_CLOUD_SANDBOX_API_TOKEN

        self.iex_client = IEXClient.Client(token, version)

    @abstractmethod
    def run(self):
        pass
