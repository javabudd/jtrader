import numpy as np
from sklearn.linear_model import LinearRegression as LineRegressionModel
from sklearn.model_selection import train_test_split

from jtrader.core.indicator.indicator import Indicator


class LinearRegression(Indicator):
    """

    """

    @staticmethod
    def get_name():
        return 'Linear Regression'

    def is_valid(self, data, comparison_data=None):
        if len(data) < self.WINDOW_SIZE_FOURTEEN:
            self.log_not_enough_data()

            return

        x = np.array([i for i in range(len(data))])
        y = np.array(data['close'].astype(float))

        x = x.reshape(-1, 1)
        y = y.reshape(-1, 1)

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

        reg = LineRegressionModel().fit(x_train, y_train)
        score = reg.score(x_test, y_test)

        if score > .95:
            pred = reg.predict(x_test)
            close = data['close'].astype(float).iloc[-1]

            predicted_fifth_day = pred[4][0]
            if predicted_fifth_day > close + (close * .02):
                return self.BULLISH
            elif predicted_fifth_day < close - (close * .02):
                return self.BEARISH
