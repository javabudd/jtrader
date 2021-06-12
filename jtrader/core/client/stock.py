from pandas import DataFrame
from pyEX.client import Client
from jtrader.core.db import DB


class StockClient:
    def __init__(self, iex_client: Client, db: DB):
        self.iex_client = iex_client
        self.db = db
        self.iex_only = True

    def get_intraday(self, ticker: str) -> DataFrame:
        return self.iex_client.stocks.intradayDF(ticker, IEXOnly=self.iex_only)

    def get_historical(self, ticker: str, day: str) -> DataFrame:
        if self.db.has_historical_stock_day(ticker, day):
            return self.db.get_historical_stock_day(ticker, day)

        # historical = self.iex_client.stocks.chart(ticker, day, timerange=range)

        # populate DB with results

    def get_technical_chart(self, ticker: str, chart_type: str, time_range: str) -> DataFrame:
        # @TODO if we have the data, don't send this request to iexcloud
        return self.iex_client.stocks.technicals(ticker, chart_type, range=time_range)

    def get_quote(self, ticker) -> DataFrame:
        pass
