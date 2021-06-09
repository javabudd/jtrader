import pandas as pd
from zipline.api import order_target, record, symbol
from zipline.protocol import BarData

from jtrader.core.validator.rsi import RSIValidator
from jtrader.core.validator.volume import VolumeValidator


def initialize(context):
    context.i = 0
    context.asset = symbol('AMZN')


def handle_data(context, data: BarData):
    bar_count = 100
    context.i += 1
    if context.i < bar_count:
        return

    high = data.history(context.asset, 'high', bar_count=bar_count, frequency="1d")
    low = data.history(context.asset, 'low', bar_count=bar_count, frequency="1d")
    close = data.history(context.asset, 'close', bar_count=bar_count, frequency="1d")
    volume = data.history(context.asset, 'volume', bar_count=bar_count, frequency="1d")

    rsi_validator = RSIValidator(context.asset)
    volume_validator = VolumeValidator(context.asset)
    data_frame = pd.DataFrame({"high": high, "low": low, "close": close, "volume": volume})

    if rsi_validator.is_valid(data_frame):
        order_target(context.asset, 5000)
    else:
        volume_validator.is_bullish = False
        rsi_validator.is_bullish = False
        if rsi_validator.is_valid(data_frame) and volume_validator.is_valid(data_frame):
            order_target(context.asset, 0)

    record(Asset=data.current(context.asset, 'close'))
