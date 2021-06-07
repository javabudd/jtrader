import talib

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
        return 'Volume'

    def is_valid(self, data=None):
        if data is None:
            data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=True)

            if 'close' not in data:
                self.log_missing_close()

                return False

        data = self.clean_dataframe(data)

        try:
            df = talib.ADOSC(data['high'], data['low'], data['close'], data['volume'])
        except Exception:
            return False

        if len(df) <= 1 or len(df) <= 1:
            return False

        if self.is_bullish:
            if df[-1] > 0 and df.iloc[:-1].mean() <= 0:
                return True
        else:
            if df[-1] < 0 and df.iloc[:-1].mean() >= 0:
                return True

        return False

    def get_validation_chain(self):
        return []
