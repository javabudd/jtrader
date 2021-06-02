import _thread
import time

import pandas as pd
from pyEX import PyEXception

import jtrader.core.utils as utils
from jtrader.core.iex import IEX
from jtrader.core.validator.apo import APOValidator
from jtrader.core.validator.ultosc import ULTOSCValidator

stocks = pd.read_csv('files/all_stocks.csv', chunksize=5000)


class Scanner(IEX):
    def run(self):
        indicators = [
            APOValidator,
            ULTOSCValidator
        ]

        while True:
            for chunk in enumerate(stocks):
                _thread.start_new_thread(self.loop, (indicators, chunk))

            time.sleep(3600)

    def loop(self, indicators, chunk):
        sleep = .5

        if self.is_sandbox:
            sleep = 2

        for ticker in chunk[1]['Ticker']:
            self.logger.info('Processing ticker: ' + ticker)
            for indicator in indicators:
                indicator_instance = indicator(ticker, self.iex_client)
                try:
                    resolved_indicator = indicator_instance.validate()
                except PyEXception as e:
                    self.logger.error(e.args[0] + ' ' + e.args[1])

                    break
                if resolved_indicator:
                    found_indicator = indicator.get_name()
                    message = ticker + ' triggered ' + found_indicator
                    self.logger.info(message)
                    utils.send_slack_message(message, '#stock-scanner')

            time.sleep(sleep)
