from abc import ABC, abstractmethod
from typing import Optional

from jtrader.core.service.iex_client import IEXClient


class IEX(ABC):
    def __init__(self, is_sandbox: bool, version: Optional[str] = 'stable'):
        self.is_sandbox = is_sandbox
        self.version = version
        self.iex_client = IEXClient(is_sandbox, version)

    @abstractmethod
    def run(self):
        pass
