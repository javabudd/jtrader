from ta.volume import VolumeWeightedAveragePrice
from pandas import DataFrame
from decimal import Decimal
import talib
from jtrader.core.indicator.indicator import Indicator


class VWAP(Indicator):
    """
    """

    @staticmethod
    def get_name():
        return 'VWAP'

    def is_valid(self, data: DataFrame, comparison_data=None):
        wopper = VolumeWeightedAveragePrice(
            data['high'].astype(float),
            data['low'].astype(float),
            data['close'].astype(float),
            data['volume'].astype(float)
        )

        vwap_df = self.clean_dataframe(wopper.vwap)

        regression = talib.LINEARREG(vwap_df, timeperiod=vwap_df.size)
        standard = talib.STDDEV(vwap_df, timeperiod=vwap_df.size)

        regression = self.clean_dataframe(regression)
        standard = self.clean_dataframe(standard)

        last_regression = Decimal(regression.iloc[-1])
        last_standard = Decimal(standard.iloc[-1])

        upper_region = last_regression + last_standard
        lower_region = last_regression - last_standard

        if vwap_df.iloc[-1] > upper_region:
            return self.BEARISH
        elif vwap_df.iloc[-1] < lower_region:
            return self.BULLISH
