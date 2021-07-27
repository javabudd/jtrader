import pandas as pd
from scipy import stats

from jtrader.core.indicator.indicator import Indicator


class LinearRegression(Indicator):
    """

    """

    @staticmethod
    def get_name():
        return 'Liner Regression'

    def is_valid(self, data, comparison_data=None):
        if len(data) < self.WINDOW_SIZE_FOURTEEN:
            self.log_not_enough_data()

            return

        n = 60

        x = data['date']
        y = data['close']
        print(data.axes)
        exit()

        print(data.to_timestamp(axis='date'))

        print(x)
        exit()

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        if slope > 0:
            # bullish check
            print(slope, r_value, p_value, intercept)
            exit()
