from typing import Optional

from cement.core.log import LogInterface

from jtrader import __CRYPTO_CSVS__
from jtrader.core.iex import IEX
from jtrader.core.validator import __VALIDATION_MAP__


class CryptoScanner(IEX):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            cryptos: Optional[str],
            indicators: Optional[list],
            time_range: Optional[str] = None
    ):
        super().__init__(is_sandbox, logger)

        self.time_range = time_range

        if cryptos is None:
            self.stock_list = __CRYPTO_CSVS__['crypto']
        else:
            if cryptos not in __CRYPTO_CSVS__:
                raise RuntimeError

            self.stock_list = __CRYPTO_CSVS__[cryptos]

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
        num_lines = len(open(self.stock_list).readlines())
        print(num_lines)
        exit()
