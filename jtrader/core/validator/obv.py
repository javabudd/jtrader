import talib

from jtrader.core.validator.validator import Validator


class OBVValidator(Validator):
    """
    Looking for pops in volume relative to time frames
    """

    @staticmethod
    def get_name():
        return 'OBV'

    def is_valid(self, data=None):
        data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=self.iex_only)

        if 'close' not in data:
            self.log_missing_close()

            return False

        self.clean_dataframe(data)

        obv = talib.OBV(data['close'], data['volume'])
        max_last_nine = max(obv[:-1][-9:])
        last = obv[-1]

        if self.is_bullish:
            print(last, max_last_nine)
            return last > 0 and max_last_nine > 0 and last - max_last_nine / max_last_nine >= .5
        else:
            return last < max_last_nine

    def get_validation_chain(self):
        return []
