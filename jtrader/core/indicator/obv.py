import talib

from jtrader.core.indicator.indicator import Indicator


class OBV(Indicator):
    """
    On-balance volume provides a running total of an asset's trading volume and indicates whether this volume is
    flowing in or out of a given security or currency pair. The OBV is a cumulative total of volume
    (positive and negative)
    """

    @staticmethod
    def get_name():
        return 'OBV'

    def is_valid(self, data, comparison_data=None):
        price_has_lower_low = self.has_lower_low(data)
        price_has_lower_high = self.has_lower_high(data)
        price_has_higher_low = self.has_higher_low(data)
        price_has_higher_high = self.has_higher_high(data)

        obv = talib.OBV(data['close'], data['volume'])

        obv_has_lower_low = obv.iloc[-1] < obv.iloc[-2]
        obv_has_higher_low = obv.iloc[-1] > obv.iloc[-2]

        if price_has_lower_low and not obv_has_lower_low or price_has_higher_low and not obv_has_higher_low:
            return self.BULLISH

        if price_has_lower_high and obv_has_lower_low or price_has_higher_high and obv_has_higher_low:
            return self.BEARISH

        return
