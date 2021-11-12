import pandas as pd

from jtrader.core.indicator.rsi import RSI


def test_get_name():
    rsi = RSI('fooBar')

    assert rsi.get_name() is 'RSI'


def test_is_valid_returns_bearish():
    rsi = RSI('fooBar')

    closes = []
    for x in range(2, 150):
        if x % 10 == 0:
            if len(closes) == 0:
                closes.append({"close": x - 2})
            else:
                last = closes[-1]['close']
                closes.append({"close": last - 1})
        else:
            closes.append({"close": x})

    data = pd.DataFrame(closes)

    assert rsi.is_valid(data) is RSI.BEARISH


def test_is_valid_returns_bullish():
    rsi = RSI('fooBar')

    closes = []
    for x in range(150, 2, -1):
        if x % 10 == 0:
            if len(closes) == 0:
                closes.append({"close": x + 2})
            else:
                last = closes[-1]['close']
                closes.append({"close": last + 1})
        else:
            closes.append({"close": x})

    data = pd.DataFrame(closes)

    assert rsi.is_valid(data) is RSI.BULLISH
