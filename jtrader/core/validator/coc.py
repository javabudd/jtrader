from jtrader.core.validator.apo import APOValidator
from jtrader.core.validator.macd import MACDValidator
from jtrader.core.validator.rsi import RSIValidator
from jtrader.core.validator.ultosc import ULTOSCValidator
from jtrader.core.validator.validator import Validator
from stockstats import StockDataFrame


class COCValidator(Validator):
    @staticmethod
    def get_name():
        return 'CoC'

    def is_valid(self):
        data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=True)

        stock = StockDataFrame.retype(data)
        print('asdf')
        exit()

        print(stock.get('macd'))

        exit()

        return True

    def get_validation_chain(self):
        return []
