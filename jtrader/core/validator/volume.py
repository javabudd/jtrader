import numpy as np

from jtrader.core.validator.validator import Validator


class VolumeValidator(Validator):
    """

    """

    @staticmethod
    def get_name():
        return 'Volume'

    def is_valid(self):
        if self.is_bullish:
            data = self.iex_client.stocks.intradayDF(self.ticker, IEXOnly=True)

            if 'close' not in data:
                self.log_missing_close()

                return False

            stock = self.data_frame_to_stock_data_frame(data)

            vr = stock.get('vr')

            vr.replace([np.inf, -np.inf], np.nan, inplace=True)
            vr.dropna(inplace=True)

            if len(vr) <= 1 or len(vr) <= 1:
                return False

            last_four = vr.tail(3)

            average_vr = last_four.head(2).mean()

            return average_vr / last_four.tail(1) > .5

        return False

    def get_validation_chain(self):
        return []