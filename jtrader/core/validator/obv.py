import talib
import pandas as pd

from jtrader.core.validator.validator import Validator


class OBVValidator(Validator):
    """
    On-balance volume provides a running total of an asset's trading volume and indicates whether this volume is
    flowing in or out of a given security or currency pair. The OBV is a cumulative total of volume
    (positive and negative)
    """

    @staticmethod
    def get_name():
        return 'OBV'

    def is_valid(self, data=None, comparison_data=None):
        if data is None:
            data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=self.iex_only)

            if 'close' not in data:
                self.log_missing_close()

                return False

        self.clean_dataframe(data)

        price_has_lower_low = self.has_lower_low(data)
        price_has_lower_high = self.has_lower_high(data)
        price_has_higher_low = self.has_higher_low(data)
        price_has_higher_high = self.has_higher_high(data)

        obv = talib.OBV(data['close'], data['volume'])
        df = pd.DataFrame(obv).reset_index()
        df.columns = ['date', 'low']

        obv_not_has_lower_low = self.has_lower_low(df) is False
        obv_not_has_higher_low = self.has_higher_low(df) is False

        df2 = pd.DataFrame(obv).reset_index()
        df2.columns = ['date', 'high']

        obv_not_has_lower_high = self.has_lower_high(df2) is False
        obv_not_has_higher_high = self.has_higher_high(df2) is False

        # if obv_has_steep_downslope or obv_has_less_steep_downslope and price_trend_not_same:
        #     return True

        # if obv_has_lower_high or obv_has_higher_high and price_trend_not_same:
        #     return True

        if price_has_lower_low and obv_not_has_lower_low or price_has_higher_low and obv_not_has_higher_low:
            return True

        if price_has_lower_high and obv_not_has_lower_high or price_has_higher_high and obv_not_has_higher_high:
            return True

        return False
