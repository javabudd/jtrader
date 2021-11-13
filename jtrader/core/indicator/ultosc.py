import talib
from pandas import DataFrame

from jtrader.core.indicator.indicator import Indicator


class ULTOSC(Indicator):
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

    def is_valid(self, data, comparison_data=None):
        if self.has_lower_low(data):
            chart = self.get_chart(data)

            if len(chart) <= 1:
                return

            highest = max(chart[:-1])
            latest = chart.iloc[-1]

            if latest > highest:
                self.result_info['value'] = latest

                return self.BULLISH
        elif self.has_higher_high(data):
            chart = self.get_chart(data)

            if len(chart) <= 1:
                return

            lowest = min(chart[:-1])
            latest = chart.iloc[-1]

            if latest < lowest:
                self.result_info['value'] = latest

                return self.BEARISH

        return

    def get_chart(self, data: DataFrame):
        chart = talib.ULTOSC(
            data['high'],
            data['low'],
            data['close'],
            timeperiod1=self.time_period,
            timeperiod2=self.time_period * 2,
            timeperiod3=self.time_period * 3
        )

        self.clean_dataframe(chart)

        return chart
