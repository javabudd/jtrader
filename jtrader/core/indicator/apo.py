import talib

from jtrader.core.indicator.indicator import Indicator


class APO(Indicator):
    """
    The Absolute Price Oscillator displays the difference between two exponential moving averages of a security's price
    and is expressed as an absolute value.

    APO crossing above zero is considered bullish , while crossing below zero is bearish . A positive indicator value
    indicates an upward movement, while negative readings signal a downward trend. Divergences form when a new high or
    low in price is not confirmed by the Absolute Price Oscillator (APO).

    Buy signals:

    A bullish divergence forms when the price makes a lower low, but the APO forms a higher low. This indicates less
    downward momentum that could foreshadow a bullish reversal.

    Sell signals:

    A bearish divergence forms when the price makes a higher high, but the APO forms a lower high. This shows less
    upward momentum that could foreshadow a bearish reversal.
    """

    @staticmethod
    def get_name():
        return 'Absolute Price Oscillator'

    def is_valid(self, data, comparison_data=None):
        if len(data) < self.WINDOW_SIZE_FOURTEEN:
            self.log_not_enough_data()

            return False

        apo_chart = talib.APO(data['close'], fastperiod=self.fast_period, slowperiod=self.slow_period)

        if self.signals_bullish(data, apo_chart):
            return self.BULLISH

        if self.signals_bearish(data, apo_chart):
            return self.BEARISH

    def signals_bullish(self, data, apo_chart):
        if self.has_lower_low(data):
            highest_apo_low = max(apo_chart[:-self.fast_period])
            latest_apo_low = apo_chart.iloc[-1]

            if latest_apo_low > highest_apo_low:
                return True

        return False

    def signals_bearish(self, data, apo_chart):
        if self.has_higher_high(data):
            lowest_apo_high = min(apo_chart[:-self.fast_period])
            latest_apo_high = apo_chart.iloc[-1]

            if latest_apo_high < lowest_apo_high:
                return True

        return False
