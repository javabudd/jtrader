import os
from typing import Optional
from typing import Union

import pandas as pd
import pyEX as IEXClient
from cement.core.log import LogInterface

from jtrader.core.provider.provider import Provider


class IEX(Provider):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            version: Optional[str] = 'stable',
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, logger, no_notifications)

        token = os.environ.get('IEX_CLOUD_API_TOKEN')
        if self.is_sandbox:
            version = 'sandbox'
            token = os.environ.get('IEX_CLOUD_SANDBOX_API_TOKEN')

        self.client_prop = IEXClient.Client(token, version)

    async def register_websockets(self, loop, ticker: str) -> None:
        return

    def chart(self, stock: str, timeframe: str) -> dict:
        return self.client.stocks.chart(stock, timeframe=timeframe)

    def symbols(self) -> dict:
        return self.client.refdata.iexSymbols()

    def technicals(
            self,
            stock: str,
            indicator_name: str,
            timeframe: str,
            as_dataframe=False
    ) -> Union[dict, pd.DataFrame]:
        if as_dataframe:
            return self.client.stocks.technicalsDF(stock, indicator_name, range=timeframe)

        return self.client.stock.technicals(stock, indicator_name, range=timeframe)
