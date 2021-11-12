import talib

from jtrader.core.indicator.indicator import Indicator


class ADX(Indicator):
    """
    ADX stands for Average Directional Movement Index and can be used to help measure the overall strength of a trend.

    The ADX indicator is an average of expanding price range values.

    The ADX is a component of the Directional Movement System developed by Welles Wilder.

    This system attempts to measure the strength of price movement in positive and negative direction using the
    DMI+ and DMI- indicators along with the ADX.

    Buy signals:

    If the +DI line crosses above the -DI line and the ADX is above 20, or ideally above 25, then that is a potential
    signal to buy.

    Sell signals:

    If the -DI crosses above the +DI, and the ADX is above 20 or 25, then that is an opportunity to enter a potential
    short trade.

    When the ADX turns down from high values, then the trend may be ending. You may want to do additional research to
    determine if closing open positions is appropriate for you.

    If the ADX is declining, it could be an indication that the market is becoming less directional, and the current
    trend is weakening. You may want to avoid trading trend systems as the trend changes.
    """

    @staticmethod
    def get_name():
        return 'ADX'

    def is_valid(self, data, comparison_data=None):
        adx = talib.ADX(data['high'], data['low'], data['close'], timeperiod=self.time_period)
        plus_di = talib.PLUS_DI(data['high'], data['low'], data['close'], timeperiod=self.time_period)
        minus_di = talib.MINUS_DI(data['high'], data['low'], data['close'], timeperiod=self.time_period)

        self.clean_dataframe(adx)
        self.clean_dataframe(plus_di)
        self.clean_dataframe(minus_di)

        if adx.empty or plus_di.empty or minus_di.empty:
            self.log_invalid_chart_length()

            return

        last_adx: float = adx.iloc[0]
        if plus_di.iloc[1] < minus_di.iloc[1] and plus_di.iloc[0] > minus_di.iloc[0] and last_adx >= 25:
            self.result_info['adx'] = round(last_adx, 2)

            return self.BULLISH

        if minus_di.iloc[1] < plus_di.iloc[1] and minus_di.iloc[0] > plus_di.iloc[0] and last_adx >= 25:
            self.result_info['adx'] = round(last_adx, 2)

            return self.BEARISH
