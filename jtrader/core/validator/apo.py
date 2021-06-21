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

    def is_valid(self, data=None, comparison_data=None):
        if self.is_bullish:
            return self.signals_bullish(data)
        else:
            return self.signals_bearish()

    def signals_bullish(self, data=None):
        if self.has_lower_low(data):
            if data is None:
                data = self.iex_client.stocks.technicals(self.ticker, 'apo', range=self.time_range)
                for required in ['chart']:
                    if required not in data:
                        self.log_missing_chart()

                        return False

                apo_chart = data['chart'][-self.WINDOW_SIZES["ten"]:]
            else:
                apo_chart = talib.APO(data['close'])

            if len(apo_chart) <= 1:
                self.log_not_enough_chart_data()

                return False

            highest_apo_low = max(apo_chart[:-1])
            latest_apo_low = apo_chart.iloc[-1]

            if latest_apo_low > highest_apo_low:
                return True

        return False

    # nothing yet
    def signals_bearish(self):
        return False
