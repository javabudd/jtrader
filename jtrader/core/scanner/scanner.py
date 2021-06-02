import _thread
import json
import time
from typing import Iterable

import pandas as pd
from pyEX import PyEXception

import jtrader.core.utils as utils
from jtrader.core.iex import IEX
from jtrader.core.validator.apo import APOValidator
from jtrader.core.validator.ultosc import ULTOSCValidator
from jtrader.core.validator.validator import Validator

stocks = pd.read_csv('files/all_stocks.csv', chunksize=5000)


class Scanner(IEX):
    def run(self):
        validators: Iterable[Validator] = [
            APOValidator,
            ULTOSCValidator
        ]

        while True:
            for chunk in enumerate(stocks):
                _thread.start_new_thread(self.loop, (validators, chunk))

            time.sleep(3600)

    def loop(self, validators, chunk):
        sleep = .5

        if self.is_sandbox:
            sleep = 2

        for ticker in chunk[1]['Ticker']:
            self.logger.info('Processing ticker: ' + ticker)
            for validator in validators:
                validator_instance = validator(ticker, self.iex_client)
                passed_validator_chains = []
                try:
                    resolved_indicator = validator_instance.validate()
                    chain = validator_instance.get_validation_chain()
                    if len(chain) > 0:
                        for validator_chain in chain:
                            if validator_chain.validate() is False:
                                return False

                            passed_validator_chains.append(validator_chain.get_name())

                except PyEXception as e:
                    self.logger.error(e.args[0] + ' ' + e.args[1])

                    break

                if len(passed_validator_chains) > 0:
                    found_indicators = json.dumps(passed_validator_chains)
                    message = ticker + ' triggered ' + found_indicators
                    self.logger.info(message)
                    utils.send_slack_message(message, '#stock-scanner')
                elif resolved_indicator:
                    found_indicator = validator.get_name()
                    message = ticker + ' triggered ' + found_indicator
                    self.logger.info(message)
                    utils.send_slack_message(message, '#stock-scanner')

            time.sleep(sleep)
