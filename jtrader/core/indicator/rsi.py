import talib

from jtrader.core.indicator.indicator import Indicator


class RSI(Indicator):
    """
    The relative strength index (RSI) is a momentum indicator used in technical analysis that measures the magnitude of
    recent price changes to evaluate overbought or oversold conditions in the price of a stock or other asset. The RSI
    is displayed as an oscillator (a line graph that moves between two extremes) and can have a reading from 0 to 100.

    Buy signals:
    Some traders will consider it a “buy signal” if a security’s RSI reading moves below 30, based on the idea that the
    security has been oversold and is therefore poised for a rebound. However, the reliability of this signal will
    depend in part on the overall context. If the security is caught in a significant downtrend, then it might continue
    trading at an oversold level for quite some time. Traders in that situation might delay buying until they see other
    confirmatory signals.

    Sell signals:

    """

    @staticmethod
    def get_name():
        return 'RSI'

    def is_valid(self, data, comparison_data=None):
        close = self.clean_dataframe(data['close'])

        if len(close) < self.time_period:
            self.log_not_enough_data()

            return

        try:
            # key 1 in the output is the smoothed line
            rsi = talib.STOCHRSI(close, timeperiod=self.time_period)[1]
        except Exception as e:
            self.log_error(e)

            return

        self.clean_dataframe(rsi)

        if len(rsi) <= 1:
            self.log_invalid_chart_length()

            return

        last_rsi = rsi.iloc[0]

        if last_rsi < 30:
            return self.BULLISH

        if last_rsi > 80:
            return self.BEARISH

        return
