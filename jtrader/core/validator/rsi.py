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
            data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=True)

            if 'close' not in data:
                return False

            data.dropna(inplace=True)

            closes = self.get_rsi(data['close'])

            return closes[-1] < 30 and np.mean(closes[:-1]) >= 30

        return False

    def get_validation_chain(self):
        return []

    @staticmethod
    def get_rsi(prices: list, n: int = 14):
        deltas = np.diff(prices)
        seed = deltas[:n + 1]
        up = seed[seed >= 0].sum() / n
        down = -seed[seed < 0].sum() / n
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100. / (1. + rs)

        for i in range(n, len(prices)):
            delta = deltas[i - 1]

            if delta > 0:
                up_delta = delta
                down_delta = 0.
            else:
                up_delta = 0.
                down_delta = -delta

            up = (up * (n - 1) + up_delta) / n
            down = (down * (n - 1) + down_delta) / n

            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

        return rsi
