class APOValidator:
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

    @staticmethod
    def validate(**kwargs):
        for required in ['indicator', 'chart']:
            if required not in kwargs.keys():
                raise RuntimeError

        indicator_data = kwargs.get('indicator')
        chart = kwargs.get('chart')

        highest_low = max(chart, key=lambda x: x["low"])
        lowest_low = min(chart, key=lambda x: x["low"])

        # @TODO update this to actual logic
        price_has_lowest_low = True

        if indicator_data[0][1] > 0 and indicator_data[0][2] <= 0:
            if price_has_lowest_low and highest_low['low'] > lowest_low['low']:
                return True

        return False
