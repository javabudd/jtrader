import math
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

__STOCK_CSVS__ = {
    'sp500': ROOT_DIR + '/files/sp_500_stocks.csv',
    'all': ROOT_DIR + '/files/all_stocks.csv'
}


def chunks(chunk_data, n: int):
    for i in range(0, len(chunk_data), n):
        yield chunk_data[i:i + n]


def chunk_stocks(stock_data: dict, is_sandbox=False, chunk_size: int = 25):
    num_lines = len(stock_data)
    chunk_size = math.floor(num_lines / chunk_size)
    if is_sandbox:
        chunk_size = math.floor(num_lines / 2)

    return chunks(stock_data, chunk_size)
