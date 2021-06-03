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

    def validate(self):
        if self.is_bullish:
            return self.signals_bullish()
        else:
            return self.signals_bearish()

    def signals_bullish(self):
        if self.has_lower_low():
            data = self.iex_client.stocks.technicals(self.ticker, 'apo', range=self.time_range)
            for required in ['chart']:
                if required not in data:
                    return False

            apo_chart = data['chart']

            if not apo_chart or len(apo_chart) == 1:
                return False

            highest_apo_low = max(apo_chart[:-1], key=lambda x: x["low"])
            latest_apo_low = apo_chart[-1]

            if latest_apo_low['low'] > highest_apo_low['low']:
                return True

        return False

    # nothing yet
    def signals_bearish(self):
        return False

    def get_validation_chain(self):
        return []
