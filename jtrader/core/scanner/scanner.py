import pandas as pd

import jtrader.core.utils as utils
from jtrader.core.iex import IEX
from jtrader.core.validator.apo import APOValidator
from jtrader.core.validator.ultosc import ULTOSCValidator

stocks = pd.read_csv('files/sp_500_stocks.csv')


class Scanner(IEX):
    def run(self):
        indicators = {
            'apo': APOValidator,
            'ultosc': ULTOSCValidator
        }

        # @TODO should we shuffle this?
        # random.shuffle(stocks['Ticker'])

        for ticker in stocks['Ticker']:
            for indicator in indicators.keys():
                data = self.send_iex_request(f"stock/{ticker}/indicator/{indicator}", {"range": "5d"})
                resolved_indicator = indicators[indicator].validate(**data)
                if resolved_indicator:
                    found_indicator = indicators[indicator].get_name()
                    utils.send_slack_message(ticker + ' triggered ' + found_indicator, '#stock-scanner')
