from typing import Optional

import pyEX as IEXClient
from cement.core.log import LogInterface

from jtrader.core.provider.provider import Provider
from jtrader.core.secrets import IEX_CLOUD_API_TOKEN, IEX_CLOUD_SANDBOX_API_TOKEN


class IEX(Provider):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            version: Optional[str] = 'stable',
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, logger, no_notifications)

        token = IEX_CLOUD_API_TOKEN
        if self.is_sandbox:
            version = 'sandbox'
            token = IEX_CLOUD_SANDBOX_API_TOKEN

        self.client = IEXClient.Client(token, version)
