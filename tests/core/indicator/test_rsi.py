import random

import pandas as pd

from jtrader.core.indicator.rsi import RSI


def test_get_name():
    rsi = RSI('fooBar')
    assert rsi.get_name() is 'RSI'

#
# def test_is_valid_returns_bearish():
#     rsi = RSI('fooBar')
#     data = pd.DataFrame({"close": random.uniform(60.00, 70.00)} for x in range(10))
#     end = pd.DataFrame({"close": random.uniform(40.00, 50.00)} for x in range(40))
#
#     data = data.append(end, ignore_index=True)
#
#     assert rsi.is_valid(data) is RSI.BEARISH


def test_is_valid_returns_bullish():
    rsi = RSI('fooBar')
    data = pd.DataFrame({"close": random.uniform(20.00, 25.00)} for x in range(20))
    end = pd.DataFrame({"close": random.uniform(40.00, 50.00)} for x in range(80))

    data = data.append(end, ignore_index=True)

    assert rsi.is_valid(data) is RSI.BULLISH
