import math
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from sklearn import linear_model
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from jtrader.core.odm import ODM
from jtrader.core.provider import Provider
from jtrader.core.trader import Trader


class Pairs(Trader):
    def __init__(self, provider: Provider, comparison_ticker: str):
        super().__init__(provider, comparison_ticker[0])
        self.odm = ODM()

    def start_trader(self):
        self.__run_detection()

    async def _on_websocket_message(self, ws, message) -> None:
        await super()._on_websocket_message(ws, message)

    def __run_detection(self):
        today = datetime.today()
        delta = 730
        start = today + relativedelta(days=-delta)
        stock_list = self.provider.symbols()

        comparison_data = pd.DataFrame(
            self.odm.get_historical_stock_range(self.ticker, start)
        )

        if len(comparison_data) <= 0:
            self.logger.warning(f"Retrieved empty data set for stock {self.ticker}")

            return

        for stock in stock_list:
            data = pd.DataFrame(
                self.odm.get_historical_stock_range(
                    stock['symbol'],
                    start
                )
            )

            if data.empty:
                self.logger.debug(f"Retrieved empty data set for stock {stock['symbol']}")

                continue

            self.__validate_regression(stock['symbol'], data, comparison_data)

    def __validate_regression(self, ticker, data, comparison_data):
        n = 60

        regr = linear_model.LinearRegression()

        x = comparison_data[['high', 'low', 'close', 'volume']].values[-n:]
        y = data['close'].to_frame().values[-n:]

        if len(x) != len(y):
            return False

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

        regr.fit(x_train, y_train)

        y_prediction = regr.predict(x_test)

        cd = r2_score(y_test, y_prediction)

        if cd > .9:
            self.logger.info(f"{ticker} qualifies with R2 score of {cd}")

            return self.__validate_regression_threshold(ticker, data, comparison_data, n)

        return False

    def __validate_regression_threshold(self, ticker, data, comparison_data, n):
        # Step 1: Generate the spread of two log price series
        # 𝑆𝑝𝑟𝑒𝑎𝑑𝑡 = log(𝑌𝑡)−(𝛼+𝛽log(𝑋𝑡))
        x2 = comparison_data['close'][-n:].astype('float')
        y2 = data['close'][-n:].astype('float')

        cov = np.cov(x2, y2)[0][1]
        variance = np.var(y2)

        beta = 1 * (cov / variance)

        current_x = x2[-1:]
        current_y = y2[-1:]

        spread = math.log(current_y) - (.05 + (beta * math.log(current_x)))

        self.logger.info(f"{ticker} has spread of {spread}")

        # Step 2: Set the range of spread series  [lower, upper]
        # If 𝑆𝑝𝑟𝑒𝑎𝑑𝑡 > 𝑢𝑝𝑝𝑒𝑟𝑡ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 Buy 𝑋𝑡, Sell  𝑌𝑡
        # If 𝑆𝑝𝑟𝑒𝑎𝑑𝑡 < 𝑙𝑜𝑤𝑒𝑟𝑡ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 Buy 𝑌𝑡, Sell  𝑋𝑡

        lower_threshold = -2
        upper_threshold = 3

        if spread > upper_threshold:
            self.logger.info(f"{ticker} SELL SELL SELL!")

            return True

        elif spread < lower_threshold:
            self.logger.debug(f"{ticker} BUY BUY BUY!")

            return True
