import talib

from jtrader.core.validator.validator import Validator


class APOValidator(Validator):
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
        if self.signals_bullish(data):
            return self.BULLISH

        if self.signals_bearish(data):
            return self.BEARISH

    def signals_bullish(self, data=None):
        if self.has_lower_low(data):
            apo_chart = talib.APO(data['close'], fastperiod=self.fast_period, slowperiod=self.slow_period)

            if len(apo_chart) <= 1:
                self.log_not_enough_chart_data()

                return False

            highest_apo_low = max(apo_chart[:-1])
            latest_apo_low = apo_chart.iloc[-1]

            if latest_apo_low > highest_apo_low:
                return True

        return False

    # nothing yet
    def signals_bearish(self, data=None):
        return False
