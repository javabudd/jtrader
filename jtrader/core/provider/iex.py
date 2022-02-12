from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional
from typing import Union

import pandas as pd
import pyEX as IEXClient

from jtrader.core.provider import Provider


class IEX(Provider):
    IEX_TECHNICAL_INDICATORS = [
        'abs', 'acos', 'ad', 'add', 'adosc', 'adx', 'ao', 'apo', 'aroon', 'aroonosc', 'asin', 'atan', 'atr',
        'avgprice', 'bbands', 'bop', 'cci', 'ceil', 'cmo', 'cos', 'cosh', 'crossany', 'crossover', 'cvi', 'decay',
        'dema', 'di', 'div', 'dm', 'dpo', 'dx', 'edecay', 'ema', 'emv', 'exp', 'fisher', 'fosc', 'hma', 'kama',
        'kvo', 'lag', 'linreg', 'linregintercept', 'linregslope', 'ln', 'log10', 'macd', 'mass', 'max',
        'md', 'medprice', 'mfi', 'min', 'mom', 'msw', 'mul', 'natr', 'nvi', 'obv', 'ppo', 'psar', 'pvi', 'qstick',
        'roc', 'rocr', 'round', 'rsi', 'sin', 'sinh', 'sma', 'sqrt', 'stddev', 'stderr', 'stoch', 'stochrsi', 'sub',
        'sum', 'tan', 'tanh', 'tema', 'todeg', 'torad', 'tr', 'trima', 'trix', 'trunc', 'tsf', 'typprice', 'ultosc',
        'var', 'vhf', 'vidya', 'volatility', 'vosc', 'vwma', 'wad', 'wcprice', 'wilders', 'willr', 'wma', 'zlema'
    ]

    IEX_TRAINABLE_INDICATORS = [
        'adosc', 'cvi', 'macd', 'obv', 'rsi', 'vwma'
    ]

    IEX_ECONOMIC_DATA = [
        'CPIUCSL'
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
        "torad": "radians",
        "CPIUCSL": "cpi_value"
    }

    IEX_DATA_POINTS = {
        'economic': IEX_ECONOMIC_DATA,
        'indicators': IEX_TRAINABLE_INDICATORS,
    }

    def __init__(
            self,
            is_sandbox: bool,
            version: Optional[str] = 'stable',
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, no_notifications)

        token = os.environ.get('IEX_CLOUD_API_TOKEN')
        if self.is_sandbox:
            version = 'sandbox'
            token = os.environ.get('IEX_CLOUD_SANDBOX_API_TOKEN')

        self.client_prop = IEXClient.Client(token, version)
        self.last_date = None

    async def register_websockets(
            self,
            loop: asyncio.AbstractEventLoop,
            ticker: str,
            on_websocket_message: callable
    ) -> None:
        raise NotImplemented

    def chart(self, stock: str, start: datetime, end: datetime | None) -> dict | list:
        return self.client.stocks.chart(stock, timeframe='1d')

    def intraday(self, stock: str) -> dict:
        return self.client.stocks.intraday(stock)

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

    def economic(self, economic_type: str, timeframe: str, as_dataframe: bool = False):
        if economic_type == 'CPI':
            now = datetime.now()
            args = {
                "id": 'ECONOMIC',
                "key": "CPIAUCSL",
                "from_": (now - timedelta(days=(365 * int(timeframe[0])))).strftime('%Y-%m-%d'),
                "to_": now.strftime('%Y-%m-%d'),
                "last": 1000,
            }

            time_diff = timedelta(days=30)
            if as_dataframe:
                frame = self.client.stocks.timeSeriesDF(**args)
                frame['date'] = frame['updated'].values

                def lam(x):
                    if self.last_date is None:
                        self.last_date = x['date']

                        return self.last_date

                    self.last_date = self.last_date - time_diff

                    return self.last_date

                frame['date'] = frame.apply(lam, axis=1)
                frame.set_index('date', inplace=True)
                frame.rename(columns={'value': 'cpi_value'}, inplace=True)

                return frame

        raise NotImplemented
