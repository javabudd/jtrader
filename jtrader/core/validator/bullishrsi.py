from jtrader.core.validator.validator import Validator


class BullishRSI(Validator):
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
        return 'Bullish RSI'

    def validate(self):
        return True

    def get_validation_chain(self):
        return []