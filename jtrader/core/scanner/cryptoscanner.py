import json
import math
import sys
import time
from threading import Thread
from typing import Optional, List

import pandas as pd
from cement.core.log import LogInterface
from cement.utils.shell import spawn_thread
from pyEX import PyEXception

import jtrader.core.utils as utils
from jtrader import __CRYPTO_CSVS__
from jtrader.core.iex import IEX
from jtrader.core.validator import __VALIDATION_MAP__


class CryptoScanner(IEX):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            indicators: Optional[list],
            time_range: Optional[str] = None
    ):
        super().__init__(is_sandbox, logger)

        self.time_range = time_range

        self.crypto_list = __CRYPTO_CSVS__['crypto']

        self.indicators = []
        if indicators is None:
            self.indicators = __VALIDATION_MAP__['all']
        else:
            for indicator in indicators:
                if indicator[0] in __VALIDATION_MAP__:
                    self.indicators.append(__VALIDATION_MAP__[indicator[0]])
            if len(self.indicators) == 0:
                raise RuntimeError

    def run(self):
        num_lines = len(open(self.crypto_list).readlines())
        chunk_size = math.floor(num_lines / 10)
        if self.is_sandbox:
            chunk_size = math.floor(num_lines / 2)

        stocks = pd.read_csv(self.crypto_list, chunksize=chunk_size)

        while True:
            i = 1
            threads: List[Thread] = []
            for chunk in enumerate(stocks):
                thread_name = f"Thread-{i}"
                """ @thread """
                thread = spawn_thread(self.loop, True, False, args=(thread_name, chunk), daemon=True)
                threads.append(thread)
                i += 1

            while len(threads) > 0:
                for thread in threads:
                    if not thread.is_alive():
                        threads.remove(thread)
                    thread.join(1)

            self.logger.info('Processing finished')
            sys.exit(1)

    def loop(self, thread_name, chunk):
        sleep = .2

        if self.is_sandbox:
            sleep = 2

        for ticker in chunk[1]['Ticker']:
            time.sleep(sleep)
            self.logger.info(f"({thread_name}) Processing crypto: {ticker}")
            for indicator_class in self.indicators:
                indicator = indicator_class(ticker, self.iex_client, self.logger)
                passed_validators = {}
                try:
                    is_valid = indicator.is_valid()

                    if is_valid is False:
                        continue

                    chain = indicator.get_validation_chain()
                    has_valid_chain = True
                    if len(chain) > 0:
                        passed_validators[indicator.get_name()] = []
                        chain_index = 0
                        for validator_chain in chain:
                            args = {}
                            if self.time_range is not None:
                                args["time_range"] = self.time_range

                            validator_chain = validator_chain(ticker, self.iex_client, self.logger, **args)
                            if validator_chain.is_valid() is False:
                                has_valid_chain = False
                                break  # break out of validation chain

                            passed_validators[indicator.get_name()].append(validator_chain.get_name())
                            chain_index += 1
                        if has_valid_chain is False:
                            continue  # continue to the next validator in list
                    else:
                        passed_validators = [indicator.get_name()]

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
                    utils.send_notification('```' + message_string + '```')

        return True
