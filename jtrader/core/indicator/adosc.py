import talib

from jtrader.core.indicator.indicator import Indicator


class ADOSC(Indicator):
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
        self.clean_dataframe(data)

        if len(data) <= 1:
            return

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
            self.log_error(e)

            return

        self.clean_dataframe(adosc)

        if len(adosc) <= 1:
            self.log_invalid_chart_length()

            return

        diff = data['close'].astype(float).diff()

        # downward price action
        if diff.iloc[-3:].sum() < 0 and diff.iloc[-6: -3].sum() > 0:
            if adosc.iloc[-2] > 0 and adosc.iloc[-1] < 0:
                return self.BEARISH

        # upward price action
        if diff.iloc[-3:].sum() > 0 and diff.iloc[-6: -3].sum() < 0:
            if adosc.iloc[-2] < 20 and adosc.iloc[-1] > 20:
                return self.BULLISH

        return
