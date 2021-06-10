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
        if self.is_bullish:
            data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=True)

            if 'close' not in data:
                self.log_missing_close()

                return False

            self.clean_dataframe(data)

            adx = talib.ADX(data['high'], data['low'], data['close'])

            return adx < 20

        return False

    def get_validation_chain(self):
        return []
