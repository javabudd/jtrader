import talib

from jtrader.core.validator.validator import Validator


class ADXValidator(Validator):
    """
    Looking for pops in volume relative to time frames
    """

    @staticmethod
    def get_name():
        return 'ADX'

    def is_valid(self, data, comparison_data=None):
        adx = talib.ADX(data['high'], data['low'], data['close'], timeperiod=self.time_period)

        self.clean_dataframe(adx)

        if adx.empty:
            return

        if adx.iloc[-1] > 20:
            return self.BULLISH

        if adx.iloc[-1] < 20:
            return self.BEARISH
