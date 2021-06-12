import pandas as pd
import talib
from scipy.cluster.vq import kmeans

from jtrader.core.validator.validator import Validator


class VolumeValidator(Validator):
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

    def is_valid(self, data=None):
        if data is None:
            data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=self.iex_only)

            if 'close' not in data:
                self.log_missing_close()

                return False

        self.clean_dataframe(data)

        try:
            adosc = talib.ADOSC(data['high'], data['low'], data['close'], data['volume'])
        except Exception:
            return False

        self.clean_dataframe(adosc)

        if len(adosc) <= 1:
            return False

        frame = pd.DataFrame(adosc.iloc[:-1]).round(0)
        centroids, _ = kmeans(frame, 2)
        resistance = max(centroids)
        support = min(centroids)

        if self.is_bullish:
            if adosc.iloc[-1] > resistance[0]:
                return True
        else:
            if adosc.iloc[-1] < support[0]:
                return True

        return False
