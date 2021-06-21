from jtrader.core.validator.validator import Validator


class ChainValidator(Validator):
    def __init__(self, ticker: str, validators: list, **kwargs):
        super().__init__(ticker, **kwargs)

        self.validators = validators

    @staticmethod
    def get_name():
        return 'Chain'

    def is_valid(self, data=None, comparison_data=None):
        return True

    def get_validation_chain(self):
        return self.validators
