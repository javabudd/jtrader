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


class Scanner(IEX):
    def run(self):
        chunk_size = 3333
        if self.is_sandbox:
            chunk_size = 6000

        stocks = pd.read_csv('files/all_stocks.csv', chunksize=chunk_size)

        validators: Iterable[Validator] = [
            RobustValidator,
        ]

        while True:
            i = 1
            for chunk in enumerate(stocks):
                _thread.start_new_thread(self.loop, (f"Thread-{i}", validators, chunk))
                i += 1

            time.sleep(3600)

    def loop(self, thread_name, validators, chunk):
        sleep = .2

        if self.is_sandbox:
            sleep = 2

        for ticker in chunk[1]['Ticker']:
            self.logger.info(f"({thread_name}) Processing ticker: {ticker}")
            for validator in validators:
                validator_instance = validator(ticker, self.iex_client)
                passed_validators = {}
                try:
                    is_valid = validator_instance.validate()

                    if is_valid is False:
                        continue

                    chain = validator_instance.get_validation_chain()
                    has_valid_chain = True
                    if len(chain) > 0:
                        passed_validators[validator_instance.get_name()] = []
                        chain_index = 0
                        for validator_chain in chain:
                            validator_chain = validator_chain(ticker, self.iex_client)
                            if validator_chain.validate() is False:
                                has_valid_chain = False
                                break  # break out of validation chain

                            passed_validators[validator_instance.get_name()].append(validator_chain.get_name())
                            chain_index += 1
                        if has_valid_chain is False:
                            continue  # continue to the next validator in list
                    else:
                        passed_validators = [validator_instance.get_name()]

                except PyEXception as e:
                    self.logger.error(e.args[0] + ' ' + e.args[1])

                    break

                if len(passed_validators) > 0:
                    message = {
                        "ticker": ticker,
                        "signal_type": "bullish",
                        "indicators_triggered": passed_validators
                    }

                    message_string = json.dumps(message)

                    self.logger.info(message_string)
                    utils.send_slack_message('```' + message_string + '```')

            time.sleep(sleep)
