import pandas as pd

from jtrader.core.indicator.rsi import RSI


def test_get_name():
    rsi = RSI('fooBar')

    assert rsi.get_name() is 'RSI'


def test_is_valid_returns_bearish():
    rsi = RSI('fooBar')
    data = pd.DataFrame({"close": 50} for x in range(90))
    end = pd.DataFrame({"close": 20} for x in range(10))

    data = data.append(end, ignore_index=True)

    assert rsi.is_valid(data) is RSI.BEARISH


def test_is_valid_returns_bullish():
    rsi = RSI('fooBar')
    data = pd.DataFrame({"close": 20} for x in range(90))
    end = pd.DataFrame({"close": 50} for x in range(10))

    data = data.append(end, ignore_index=True)

    assert rsi.is_valid(data) is RSI.BULLISH
