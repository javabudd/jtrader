import time

import pandas as pd

import jtrader.core.utils as utils
from jtrader.core.iex import IEX
from jtrader.core.validator.apo import APOValidator
from jtrader.core.validator.ultosc import ULTOSCValidator

stocks = pd.read_csv('files/all_stocks.csv')


class Scanner(IEX):
    def run(self):
        indicators = [
            APOValidator,
            ULTOSCValidator
        ]

        while True:
            randomized_stocks = stocks.sample(frac=1)

            for ticker in randomized_stocks['Ticker']:
                for indicator in indicators:
                    indicator_instance = indicator(ticker, self.iex_client)
                    resolved_indicator = indicator_instance.validate()
                    if resolved_indicator:
                        found_indicator = indicator.get_name()
                        utils.send_slack_message(ticker + ' triggered ' + found_indicator, '#stock-scanner')

            utils.send_slack_message('Scanner pass-through, sleeping for 60 minutes', '#stock-scanner')
            time.sleep(3600)
