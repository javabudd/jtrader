import pandas as pd

from jtrader.core.indicator.adx import ADX


def test_get_name():
    rsi = ADX('fooBar')

    assert rsi.get_name() is 'ADX'


def test_is_valid_returns_bearish():
    adx = ADX('fooBar')
    price = 150
    data = pd.DataFrame(
        {
            "high": price + (x / 1.5),
            "low": price - (x / 1.5),
            "close": price + (x / 1.5)
        } for x in range(1, 50)
    )

    last = data.iloc[-1]['close']

    offset = 4
    data = data.append(
        {
            "high": last + offset,
            "low": last + offset,
            "close": last + offset
        },
        ignore_index=True
    )

    data = data.append(
        {
            "high": last - offset,
            "low": last - offset,
            "close": last - offset
        },
        ignore_index=True
    )

    assert adx.is_valid(data) is ADX.BEARISH


def test_is_valid_returns_bullish():
    adx = ADX('fooBar')
    price = 150
    data = pd.DataFrame(
        {
            "high": price + (x / 1.5),
            "low": price - (x / 1.5),
            "close": price + (x / 1.5)
        } for x in range(1, 50)
    )

    last = data.iloc[-1]['close']

    offset = 4
    data = data.append(
        {
            "high": last - offset,
            "low": last - offset,
            "close": last - offset
        },
        ignore_index=True
    )

    data = data.append(
        {
            "high": last + offset,
            "low": last + offset,
            "close": last + offset
        },
        ignore_index=True
    )

    assert adx.is_valid(data) is ADX.BULLISH
