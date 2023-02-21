from __future__ import annotations

import asyncio
import csv
import os
from datetime import datetime
from typing import Optional

import requests
from alpha_vantage.timeseries import TimeSeries

from jtrader.core.provider import Provider


class AlphaVantage(Provider):
    def __init__(
            self,
            is_sandbox: bool,
            version: Optional[str] = 'stable',
            no_notifications: Optional[bool] = False
    ):
        super().__init__(is_sandbox, no_notifications)

        self.client_prop = TimeSeries(key=os.environ.get('ALPHAVANTAGE_API_KEY'), output_format='pandas')

    def chart(self, stock: str, start: datetime | None, end: datetime | None, timeframe: str) -> dict | list:
        print(start, timeframe)
        exit()
        try:
            chart = self.client.get_daily(stock)
        except ValueError as e:
            if 'Our standard API call frequency' in e.args[0]:
                os.sleep(30)

                return self.chart(stock, start, end, timeframe)

        print(chart)
        exit()

        return chart

    def economic(self, economic_type: str, timeframe: str, as_dataframe: bool = False):
        pass

    def intraday(self, stock: str) -> dict:
        pass

    def symbols(self) -> dict:
        csv_url = \
            f"https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={os.environ.get('ALPHAVANTAGE_API_KEY')}"

        with requests.Session() as s:
            download = s.get(csv_url)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            csv_list = list(cr)
            symbols = []
            csv_list.pop(0)
            for row in csv_list:
                symbols.append({
                    "symbol": row[0],
                    "isEnabled": row[6] == 'Active'
                })

        return symbols

    def register_websockets(
            self,
            loop: asyncio.AbstractEventLoop,
            ticker: str,
            on_websocket_message: callable
    ) -> None:
        pass
