import pandas as pd

import jtrader.core.utils as utils
from jtrader.core.iex import IEX

stocks = pd.read_csv('files/sp_500_stocks.csv')


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

    @staticmethod
    def get_name():
        return 'Ultimate Oscillator'

    @staticmethod
    def validate(**kwargs):
        if 'indicator' not in kwargs.keys():
            raise RuntimeError

        indicator_data = kwargs.get('indicator')
        short_period = indicator_data[0][0]
        medium_period = indicator_data[0][1]
        long_period = indicator_data[0][2]

        if short_period is None or medium_period is None or long_period is None:
            return False

        return long_period >= 70 and medium_period >= 50 and short_period >= 30


class Scanner(IEX):
    def run(self):
        indicators = {
            'apo': APOValidator,
            'ultosc': ULTOSCValidator
        }

        # @TODO should we shuffle this?
        # random.shuffle(stocks['Ticker'])

        for ticker in stocks['Ticker']:
            for indicator in indicators.keys():
                data = self.send_iex_request(f"stock/{ticker}/indicator/{indicator}", {"range": "5d"})
                resolved_indicator = indicators[indicator].validate(**data)
                if resolved_indicator:
                    found_indicator = indicators[indicator].get_name()
                    utils.send_slack_message(ticker + ' triggered ' + found_indicator, '#stock-scanner')
