import pandas as pd
import talib
from scipy.cluster.vq import kmeans

from jtrader.core.indicator.indicator import Indicator


class Volume(Indicator):
    """
    The Chaikin Oscillator is essentially a momentum indicator, but of the Accumulation-Distribution line rather than
    merely price. It looks at both the strength of price moves and the underlying buying and selling pressure during a
    given time period.

    Buy signals:
    A Chaikin Oscillator reading above zero indicates net buying pressure, while one below zero registers net selling
    pressure. Divergence between the indicator and pure price moves are the most common signals from the indicator, and
    often flag market turning points.

    Sell signals:

    """

    @staticmethod
    def get_name():
        return 'ADOSC (Chaikin Oscillator))'

    def is_valid(self, data, comparison_data=None):
        try:
            adosc = talib.ADOSC(
                data['high'],
                data['low'],
                data['close'],
                data['volume'],
                fastperiod=self.fast_period,
                slowperiod=self.slow_period
            )
        except Exception as e:
            self.logger.error(e)

            return

        self.clean_dataframe(adosc)

        if len(adosc) <= 1:
            self.logger.error(f"{self.ticker} has an ADOSC length of <= 1")

            return

        frame = pd.DataFrame(adosc.iloc[:-1]).round(0)

        try:
            centroids, _ = kmeans(frame, 2)
        except ValueError as e:
            self.logger.error(e)

            return

        resistance = max(centroids)
        support = min(centroids)

        if adosc.iloc[-self.fast_period:].mean() > resistance[0]:
            return self.BULLISH

        if adosc.iloc[-self.fast_period:].mean() < support[0]:
            return self.BEARISH

        return
