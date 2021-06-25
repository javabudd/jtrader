import math

import pandas as pd

CSV_COLUMNS = [
    'ticker',
    'date',
    'close',
    'high',
    'low',
    'open',
    'volume',
    'updated',
    'changeOverTime',
    'marketChangeOverTime',
    'uOpen',
    'uClose',
    'uHigh',
    'uLow',
    'uVolume',
    'fOpen',
    'fClose',
    'fHigh',
    'fLow',
    'fVolume',
    'change',
    'changePercent'
]


def get_stocks_chunked(stock_list, is_sandbox=False):
    num_lines = len(open(stock_list).readlines())
    chunk_size = math.floor(num_lines / 25)
    if is_sandbox:
        chunk_size = math.floor(num_lines / 2)

    return pd.read_csv(stock_list, chunksize=chunk_size)
