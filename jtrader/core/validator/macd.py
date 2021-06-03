import numpy as np

from jtrader.core.validator.validator import Validator


class MACDValidator(Validator):
    """
    Moving average convergence divergence (MACD) is a trend-following momentum indicator that shows the relationship
    between two moving averages of a security’s price. The MACD is calculated by subtracting the 26-period exponential
    moving average (EMA) from the 12-period EMA. The result of that calculation is the MACD line. A nine-day EMA of
    the MACD called the "signal line," is then plotted on top of the MACD line, which can function as a trigger for
    buy and sell signals. Traders may buy the security when the MACD crosses above its signal line and sell—or
    short—the security when the MACD crosses below the signal line. Moving average convergence divergence (MACD)
    indicators can be interpreted in several ways, but the more common methods are crossovers, divergences, and rapid
    rises/falls.

    Buy signals:
    A bullish divergence appears when the MACD forms two rising lows that correspond with two falling lows on the price.
    This is a valid bullish signal when the long-term trend is still positive.

    Sell signals:
    When the MACD forms a series of two falling highs that correspond with two rising highs on the price, a bearish
    divergence has been formed. A bearish divergence that appears during a long-term bearish trend is considered
    confirmation that the trend is likely to continue.
    """

    @staticmethod
    def get_name():
        return 'MACD'

    def is_valid(self):
        if self.is_bullish:
            data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=True)

            if 'close' not in data:
                return False

            data.dropna(inplace=True)

            closes = data['close']

            macd = self.get_macd(closes)
            signal_line = self.get_ema(9, macd)

            average_mac = np.mean(macd[:-1])
            average_ema = np.mean(signal_line[:-1])

            return macd[-1] > signal_line[-1] and average_mac <= average_ema

        return False

    def get_validation_chain(self):
        return []

    def get_macd(self, closes: list, slow: int = 26, fast: int = 12):
        emas_low = self.get_ema(slow, closes)
        ema_fast = self.get_ema(fast, closes)

        return ema_fast - emas_low
