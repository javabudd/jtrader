import numpy as np

from jtrader.core.validator.validator import Validator


class RSIValidator(Validator):
    """
    The relative strength index (RSI) is a momentum indicator used in technical analysis that measures the magnitude of
    recent price changes to evaluate overbought or oversold conditions in the price of a stock or other asset. The RSI
    is displayed as an oscillator (a line graph that moves between two extremes) and can have a reading from 0 to 100.

    Buy signals:
    Some traders will consider it a “buy signal” if a security’s RSI reading moves below 30, based on the idea that the
    security has been oversold and is therefore poised for a rebound. However, the reliability of this signal will
    depend in part on the overall context. If the security is caught in a significant downtrend, then it might continue
    trading at an oversold level for quite some time. Traders in that situation might delay buying until they see other
    confirmatory signals.

    Sell signals:

    """

    @staticmethod
    def get_name():
        return 'RSI'

    def validate(self):
        if self.is_bullish:
            data = self.iex_client.stocks.technicals(self.ticker, 'rsi', range=self.time_range)

            if 'chart' not in data:
                return False

            chart = data['chart']

            if not chart or len(chart) == 1:
                return False

            average_close = np.mean(list(map(lambda x: x['close'], chart)))

            return average_close <= 30

        return False

    def get_validation_chain(self):
        return []
