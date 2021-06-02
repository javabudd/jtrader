import _thread
import json
import time
from typing import Iterable

import pandas as pd
from pyEX import PyEXception

import jtrader.core.utils as utils
from jtrader.core.iex import IEX
from jtrader.core.validator.robust import RobustValidator
from jtrader.core.validator.validator import Validator

stocks = pd.read_csv('files/all_stocks.csv', chunksize=5000)


class Scanner(IEX):
    def run(self):
        validators: Iterable[Validator] = [
            RobustValidator
        ]

        while True:
            for chunk in enumerate(stocks):
                _thread.start_new_thread(self.loop, (validators, chunk))

            time.sleep(3600)

    def loop(self, validators, chunk):
        sleep = .25

        if self.is_sandbox:
            sleep = 2

        for ticker in chunk[1]['Ticker']:
            self.logger.info('Processing ticker: ' + ticker)
            for validator in validators:
                validator_instance = validator(ticker, self.iex_client)
                passed_validator_chains = []
                try:
                    resolved_indicator = validator_instance.validate()

                    if resolved_indicator is False:
                        continue
                    chain = validator_instance.get_validation_chain()
                    has_valid_chain = True
                    if len(chain) > 0:
                        passed_validator_chains.append(validator_instance.get_name())
                        for validator_chain in chain:
                            validator_chain = validator_chain(ticker, self.iex_client)
                            if validator_chain.validate() is False:
                                has_valid_chain = False
                                break  # break out of validation chain

                            passed_validator_chains.append(validator_chain.get_name())
                        if has_valid_chain is False:
                            continue  # continue to the next validator in list

                except PyEXception as e:
                    self.logger.error(e.args[0] + ' ' + e.args[1])

                    break

                found_indicator = None
                if len(passed_validator_chains) > 0:
                    found_indicator = json.dumps(passed_validator_chains)
                elif resolved_indicator:
                    found_indicator = validator.get_name()

                if found_indicator is not None:
                    message = ticker + ' triggered ' + found_indicator
                    self.logger.info(message)
                    utils.send_slack_message(message, '#stock-scanner')

            time.sleep(sleep)
