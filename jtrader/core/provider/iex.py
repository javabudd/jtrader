import os
from typing import Optional
from typing import Union

import pandas as pd
import pyEX as IEXClient
from cement.core.log import LogInterface

from jtrader.core.provider.provider import Provider


class IEX(Provider):
    IEX_TECHNICAL_INDICATORS = [
        'abs', 'acos', 'ad', 'add', 'adosc', 'adx', 'ao', 'apo', 'aroon', 'aroonosc', 'asin', 'atan', 'atr',
        'avgprice', 'bbands', 'bop', 'cci', 'ceil', 'cmo', 'cos', 'cosh', 'crossany', 'crossover', 'cvi', 'decay',
        'dema', 'di', 'div', 'dm', 'dpo', 'dx', 'edecay', 'ema', 'emv', 'exp', 'fisher', 'floor', 'fosc', 'hma', 'kama',
        'kvo', 'lag', 'linreg', 'linregintercept', 'linregslope', 'ln', 'log10', 'macd', 'mass', 'max',
        'md', 'medprice', 'mfi', 'min', 'mom', 'msw', 'mul', 'natr', 'nvi', 'obv', 'ppo', 'psar', 'pvi', 'qstick',
        'roc', 'rocr', 'round', 'rsi', 'sin', 'sinh', 'sma', 'sqrt', 'stddev', 'stderr', 'stoch', 'stochrsi', 'sub',
        'sum', 'tan', 'tanh', 'tema', 'todeg', 'torad', 'tr', 'trima', 'trix', 'trunc', 'tsf', 'typprice', 'ultosc',
        'var', 'vhf', 'vidya', 'volatility', 'vosc', 'vwma', 'wad', 'wcprice', 'wilders', 'willr', 'wma', 'zlema'
    ]

    SPECIAL_INDICATORS = {
        "adx": "dx",
        "aroon": "aroon_up",
        "bbands": "bbands_upper",
        "di": "plus_di",
        "dm": "plus_dm",
        "dpo": "dop",
        "msw": "msw_lead",
        "natr": "matr",
        "stoch": "stock_k",
        "todeg": "degrees",
        "torad": "radians"
    }

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
