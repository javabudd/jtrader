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

    Wilder suggests that a strong trend is present when ADX is above 25 and no trend is present when below 20.

    Sell signals:

    Wilder suggests that a strong trend is present when ADX is above 25 and no trend is present when below 20.

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

        self.clean_dataframe(adx)

        if adx.empty:
            self.log_invalid_chart_length()

            return

        last_adx: float = adx.iloc[0]
        average = adx.iloc[1:6]
        average_adx = average.mean()

        if last_adx >= 25 and average_adx < 25:
            self.result_info['adx'] = round(last_adx, 2)

            return self.BULLISH

        if last_adx <= 20 and average_adx > 20:
            self.result_info['adx'] = round(last_adx, 2)

            return self.BEARISH
