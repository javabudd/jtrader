from typing import Optional

from jtrader.core.service.iex_client import IEXClient


class ULTOSCValidator:
    """
    The Ultimate Oscillator is a range-bound indicator with a value that fluctuates between 0 and 100. Similar to the
    Relative Strength Index (RSI), levels below 30 are deemed to be oversold, and levels above 70 are deemed to be
    overbought. Trading signals are generated when the price moves in the opposite direction as the indicator, and are
    based on a three-step method.

    Buy signals:

    First, a bullish divergence must form. This is when the price makes a lower low but the indicator is at a higher
    low.Second, the first low in the divergence (the lower one) must have been below 30. This means the divergence
    started from oversold territory and is more likely to result in an upside price reversal. Third, the Ultimate
    oscillator must rise above the divergence high. The divergence high is the high point between the two lows of
    the divergence.

    Sell signals:

    First, a bearish divergence must form. This is when the price makes a higher high but the indicator is at a lower
    high. Second, the first high in the divergence (the higher one) must be above 70. This means the divergence started
    from overbought territory and is more likely to result in a downside price reversal. Third, the Ultimate oscillator
    must drop below the divergence low. The divergence low is the low point between the two highs of the divergence.
    """

    def __init__(self, ticker: str, iex_client: IEXClient, is_bullish: Optional[bool] = True):
        self.iex_client = iex_client
        self.ticker = ticker
        self.is_bullish = is_bullish

    @staticmethod
    def get_name():
        return 'Ultimate Oscillator'

    def validate(self):
        time_range = '5d'
        data = self.iex_client.send_iex_request(f"stock/{self.ticker}/indicator/ultosc", {"range": time_range})
        if 'indicator' not in data:
            return False

        indicator_data = data['indicator']

        if 0 not in indicator_data[0] or indicator_data[0][0] is None:
            return False

        if 1 not in indicator_data[0] or indicator_data[0][1] is None:
            return False

        if 2 not in indicator_data[0] or indicator_data[0][2] is None:
            return False

        short_period = indicator_data[0][0]
        medium_period = indicator_data[0][1]
        long_period = indicator_data[0][2]

        if short_period is None or medium_period is None or long_period is None:
            return False

        return long_period >= 70 and medium_period >= 50 and short_period >= 30
