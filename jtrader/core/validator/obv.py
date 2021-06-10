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
        data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=True)

        if 'close' not in data:
            self.log_missing_close()

            return False

        self.clean_dataframe(data)

        adx = talib.ADX(data['high'], data['low'], data['close'])

        if self.is_bullish:
            return adx > 20
        else:
            return adx < 20

    def get_validation_chain(self):
        return []
