from jtrader.core.validator.validator import Validator


class ULTOSCValidator(Validator):
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

    def is_valid(self, data=None):
        if self.is_bullish:
            if self.has_lower_low():
                data = self.iex_client.stocks.technicals(self.ticker, 'ultosc', range=self.time_range)

                if 'chart' not in data:
                    self.log_missing_chart()

                    return False

                chart = data['chart']

                if not chart or len(chart) == 1:
                    self.log_not_enough_chart_data()

                    return False

                highest_low = max(chart[:-1], key=lambda x: x["low"] is not None)
                lowest_low = min(chart, key=lambda x: x["low"] is not None)
                latest_low = chart[-1]

                if latest_low['low'] > highest_low['low'] and lowest_low['low'] < 30:
                    return True

        return False

    def get_validation_chain(self):
        return []
