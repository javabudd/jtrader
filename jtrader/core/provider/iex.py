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
    IEX_DATA_TYPE_ECONOMICS = 'economics'
    IEX_DATA_TYPE_INDICATOR = 'indicators'

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

    IEX_TRAINABLE_ECONOMICS = [
        'CPIAUCSL', 'RECPROUSM156N', 'UNRATE', 'A191RL1Q225SBEA'
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
        "CPIAUCSL": "cpi_value",
        "UNRATE": "unrate_value",
        "RECPROUSM156N": "recession_prob_value",
        "A191RL1Q225SBEA": "gdp_value"
    }

    IEX_TRAINABLE_DATA_POINTS = {
        IEX_DATA_TYPE_ECONOMICS: IEX_TRAINABLE_ECONOMICS,
        IEX_DATA_TYPE_INDICATOR: IEX_TRAINABLE_INDICATORS,
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

    def chart(self, stock: str, start: datetime | None, end: datetime | None, timeframe='1d') -> dict | list:
        return self.client.stocks.chart(stock, timeframe=timeframe)

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
        assert economic_type in self.SPECIAL_INDICATORS

        now = datetime.now()
        args = {
            "id": 'ECONOMIC',
            "key": economic_type,
            "from_": (now - timedelta(days=(365 * int(timeframe[0])))).strftime('%Y-%m-%d'),
            "to_": now.strftime('%Y-%m-%d'),
            "last": 1000,
        }

        def create_frame(frame_args: dict):
            f = self.client.stocks.timeSeriesDF(**frame_args)
            f['date'] = f['updated'].values
            f['date'] = f.apply(self.adjust_economic_dates, axis=1)
            f['date'] = pd.to_datetime(f['date'].dt.strftime('%Y-%m-%d'))
            f.set_index('date', inplace=True)

            return f

        if as_dataframe:
            frame = create_frame(args)
            frame.rename(columns={'value': self.SPECIAL_INDICATORS[economic_type]}, inplace=True)

            return frame

        raise NotImplemented

    def adjust_economic_dates(self, x):
        if self.last_date is None:
            self.last_date = x['date']

            return self.last_date

        self.last_date = self.last_date - timedelta(days=30)

        return self.last_date
