import pandas as pd

from jtrader.core.indicator.adx import ADX


def test_get_name():
    rsi = ADX('fooBar')

    assert rsi.get_name() is 'ADX'


def test_is_valid_returns_bearish():
    adx = ADX('fooBar')

    closes = []

    data = pd.DataFrame({"high": x, "low": x - 1, "close": x} for x in range(100, 200))

    assert adx.is_valid(data) is ADX.BEARISH
