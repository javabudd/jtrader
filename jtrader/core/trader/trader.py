from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from logging import getLogger

import pandas as pd

from jtrader.core.indicator import __INDICATOR_MAP__
from jtrader.core.indicator.chain import Chain
from jtrader.core.indicator.indicator import Indicator
from jtrader.core.provider import Provider


class Trader(ABC):
    KLINE_COLUMNS = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']

    def __init__(self, provider: Provider, ticker: str):
        self.provider = provider
        self.ticker = ticker
        self.frames: pd.Dataframe | None = None
        self.logger = getLogger()

    def start_trader(self):
        self.logger.info('looking up previous data...')

        date = datetime.now()
        start = date - timedelta(days=1)
        previous = self.provider.chart(self.ticker, start, None)

        self.frames = pd.concat(
            [pd.DataFrame(previous, columns=self.KLINE_COLUMNS)],
            ignore_index=True
        )

        self.provider.connect_websocket(self.ticker, self._on_websocket_message)

    @abstractmethod
    async def _on_websocket_message(self, ws, message) -> None:
        raise NotImplemented

    def _execute_chain_validation(self):
        chain = Chain(self.ticker, __INDICATOR_MAP__['all'])

        for validator in chain.get_validation_chain(True):
            is_valid = validator.is_valid(self.frames)

            if is_valid is not None:
                if is_valid == Indicator.BULLISH:
                    self.logger.info(validator.get_name() + ': BULLISH')
                elif is_valid == Indicator.BEARISH:
                    self.logger.warning(validator.get_name() + ': BEARISH')
