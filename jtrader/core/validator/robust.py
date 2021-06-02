from jtrader.core.validator.apo import APOValidator
from jtrader.core.validator.bullishrsi import BullishRSI
from jtrader.core.validator.ultosc import ULTOSCValidator
from jtrader.core.validator.validator import Validator


class RobustValidator(Validator):
    @staticmethod
    def get_name():
        return 'Robust (Chain)'

    def validate(self):
        return True

    def get_validation_chain(self):
        return [
            BullishRSI,
            APOValidator,
            ULTOSCValidator
        ]
