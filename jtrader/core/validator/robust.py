from jtrader.core.validator.apo import APOValidator
from jtrader.core.validator.macd import MACDValidator
from jtrader.core.validator.rsi import RSIValidator
from jtrader.core.validator.ultosc import ULTOSCValidator
from jtrader.core.validator.validator import Validator


class RobustValidator(Validator):
    @staticmethod
    def get_name():
        return 'Robust (Chain)'

    def is_valid(self, data=None):
        return True

    def get_validation_chain(self):
        return [
            RSIValidator,
            MACDValidator,
            APOValidator,
            ULTOSCValidator
        ]
