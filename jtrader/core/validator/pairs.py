import math

import numpy as np
from sklearn import linear_model
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from jtrader.core.validator.validator import Validator


class PairsValidator(Validator):
    """
    """

    @staticmethod
    def get_name():
        return 'Pairs'

    def is_valid(self, data=None, comparison_data=None):
        if data is None:
            return False

        regr = linear_model.LinearRegression()

        x = comparison_data[['high', 'low', 'close', 'volume']].values[-500:]
        y = data['close'].to_frame().values[-500:]

        if len(x) != len(y):
            return False

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

        regr.fit(x_train, y_train)

        y_prediction = regr.predict(x_test)

        cd = r2_score(y_test, y_prediction)

        if cd > .9:
            # Step 1: Generate the spread of two log price series
            # 𝑆𝑝𝑟𝑒𝑎𝑑𝑡 = log(𝑌𝑡)−(𝛼+𝛽log(𝑋𝑡))
            x2 = comparison_data['close']
            y2 = data['close']

            cov = np.cov(x2, y2)[0][1]
            variance = np.var(y2)

            beta = 1 * (cov / variance)

            current_x = x2[-1:]
            current_y = y2[-1:]

            spread = math.log(current_y) - (.05 + (beta * math.log(current_x)))

            lower_threshold = -2
            upper_threshold = 3

            # Step 2: Set the range of spread series  [lower, upper]
            # If 𝑆𝑝𝑟𝑒𝑎𝑑𝑡 > 𝑢𝑝𝑝𝑒𝑟𝑡ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 Buy 𝑋𝑡, Sell  𝑌𝑡
            # If 𝑆𝑝𝑟𝑒𝑎𝑑𝑡 < 𝑙𝑜𝑤𝑒𝑟𝑡ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 Buy 𝑌𝑡, Sell  𝑋𝑡

            # if self.is_bullish:
            if spread > upper_threshold:
                print('sell sell sell')
                print(cd)

                return True

            elif spread < lower_threshold:
                print('buy buy buy')
                print(cd)

                return True

        return False
