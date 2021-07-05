import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

__STOCK_CSVS__ = {
    'sp500': ROOT_DIR + '/files/sp_500_stocks.csv',
    'all': ROOT_DIR + '/files/all_stocks.csv'
}
