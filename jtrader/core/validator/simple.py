from jtrader.core.validator.rsi import RSIValidator
from jtrader.core.validator.validator import Validator
from jtrader.core.validator.volume import VolumeValidator


class SimpleValidator(Validator):
    @staticmethod
    def get_name():
        return 'Simple (Chain)'

    def is_valid(self, data=None):
        return True

    def get_validation_chain(self):
        return [
            VolumeValidator,
            RSIValidator
        ]
