import talib

from jtrader.core.validator.validator import Validator


class ADXValidator(Validator):
    """
    Looking for pops in volume relative to time frames
    """

    @staticmethod
    def get_name():
        return 'ADX'

    def is_valid(self, data=None):
        if data is None:
            data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=self.iex_only)

            if 'close' not in data:
                self.log_missing_close()

                return False

        adx = talib.ADX(data['high'], data['low'], data['close'])

        self.clean_dataframe(adx)

        if adx.empty:
            return False

        if self.is_bullish:
            return adx.iloc[-1] > 20
        else:
            return adx.iloc[-1] < 20
