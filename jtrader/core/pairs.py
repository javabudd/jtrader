import math
from datetime import datetime

import numpy as np
import pandas as pd
from cement.core.log import LogInterface
from dateutil.relativedelta import relativedelta
from sklearn import linear_model
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from jtrader import __STOCK_CSVS__
from jtrader.core.odm import ODM
from jtrader.core.utils.csv import get_stocks_chunked


class Pairs:
    """
    """

    def __init__(
            self,
            logger: LogInterface,
            comparison_ticker: str
    ):
        self.logger = logger
        self.odm = ODM()
        self.comparison_ticker = comparison_ticker[0]

    def run_detection(self):
        today = datetime.today()
        delta = 730
        start = today + relativedelta(days=-delta)
        stock_list = __STOCK_CSVS__['all']

        stocks = get_stocks_chunked(stock_list)

        comparison_data = pd.DataFrame(
            self.odm.get_historical_stock_range(self.comparison_ticker, start)
        )

        if len(comparison_data) <= 0:
            self.logger.warning(f"Retrieved empty data set for stock {self.comparison_ticker}")

            return

        for chunk in enumerate(stocks):
            for stock in chunk[1]['Ticker']:
                data = pd.DataFrame(
                    self.odm.get_historical_stock_range(
                        stock,
                        start
                    )
                )

                if data.empty:
                    self.logger.debug(f"Retrieved empty data set for stock {stock}")

                    continue

                self.validate_regression(stock, data, comparison_data)

    def validate_regression(self, ticker, data, comparison_data):
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

            return self.validate_regression_threshold(ticker, data, comparison_data, n)

        return False

    def validate_regression_threshold(self, ticker, data, comparison_data, n):
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

        # if self.is_bullish:
        if spread > upper_threshold:
            self.logger.info(f"{ticker} SELL SELL SELL!")

            return True

        elif spread < lower_threshold:
            self.logger.debug(f"{ticker} BUY BUY BUY!")

            return True