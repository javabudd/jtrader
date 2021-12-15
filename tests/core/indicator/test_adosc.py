import pandas as pd

from jtrader.core.indicator.adosc import ADOSC


def test_get_name():
    adosc = ADOSC('fooBar')

    assert adosc.get_name() is 'ADOSC'


def test_is_valid_returns_bearish():
    adosc = ADOSC('fooBar')
    price = 150
    volume = 10
    data = pd.DataFrame(
        {
            "high": price + (x / 1.5),
            "low": price - (x / 1.5),
            "close": price + (x / 1.5),
            "volume": (volume + x) * 2
        } for x in range(1, 50)
    )

    last = data.iloc[-1]['close']
    last_volume = data.iloc[-1]['volume']

    multiplier = 10
    for x in range(1, 3):
        data = data.append(
            {
                "high": last - (x * multiplier),
                "low": last - (x * multiplier),
                "close": last - (x * multiplier),
                "volume": (last_volume - x) * multiplier
            },
            ignore_index=True
        )

    for x in range(-4, -10, -1):
        data.iloc[x]['volume'] = (data.iloc[x]['volume'] - x) * (multiplier * 2)

    assert adosc.is_valid(data) is ADOSC.BEARISH

#
# def test_is_valid_returns_bullish():
#     adosc = ADOSC('fooBar')
#
#     assert adosc.is_valid(data) is ADOSC.BULLISH
