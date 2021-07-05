#!/usr/bin/env python
# coding: utf-8

import io
import time

import pandas as pd

from jtrader import __STOCK_CSVS__
from jtrader.core.provider.iex import IEX

relative_volume = 'Relative Volume (30 Day)'
change_from_close = 'Change From Close (%)'
gap = 'Gap(%)'

csv_columns = [
    'Ticker',
    'Price',
    'Volume Today',
    'Shares Outstanding',
    relative_volume,
    gap,
    change_from_close,
    'News'
]


class PreMarketMomentum(IEX):
    def run(self):
        stocks = pd.read_csv(__STOCK_CSVS__['all'])

        symbol_groups = list(self.chunks(stocks['Ticker'], 100))
        symbol_strings = []
        for i in range(0, len(symbol_groups)):
            symbol_strings.append(','.join(symbol_groups[i]))

        series = []
        for symbol_string in symbol_strings:
            data = self.client.stocks.batch(symbol_string, ['quote', 'stats'])
            for symbol in symbol_string.split(','):
                if symbol not in data:
                    continue

                if self.stock_qualifies(data[symbol]):
                    news = None
                    if 'news' in data[symbol]['quote']:
                        news = data[symbol]['quote']['news']

                    series.append(
                        pd.Series(
                            [
                                symbol,
                                data[symbol]['quote']['extendedPrice'],
                                data[symbol]['quote']['latestVolume'],
                                data[symbol]['stats']['sharesOutstanding'],
                                (data[symbol]['quote']['latestVolume'] - data[symbol]['quote']['avgTotalVolume'])
                                / data[symbol]['quote']['avgTotalVolume'],
                                data[symbol]['quote']['extendedChangePercent'],
                                data[symbol]['quote']['changePercent'],
                                news
                            ],
                            index=csv_columns
                        )
                    )

        df = pd.DataFrame(series, columns=csv_columns)

        if df.empty:
            self.logger.info('No stocks on PMM radar')

            return

        df.sort_values([gap, 'Volume Today'], ascending=False, inplace=True)
        df.reset_index(inplace=True, drop=True)

        file_name = 'PreMarketMomentum.xlsx'

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        df.to_excel(writer, 'PMM', index=False)

        bg_color = '#0a0a23'
        font_color = '#ffffff'

        string_format = writer.book.add_format(
            {
                'font_color': font_color,
                'bg_color': bg_color,
                'border': 1
            }
        )

        dollar_format = writer.book.add_format(
            {
                'font_color': font_color,
                'bg_color': bg_color,
                'border': 1,
                'num_format': '$0.00'
            }
        )

        float_format = writer.book.add_format(
            {
                'font_color': font_color,
                'bg_color': bg_color,
                'border': 1,
                'num_format': '0.00'
            }
        )

        percent_format = writer.book.add_format(
            {
                'font_color': font_color,
                'bg_color': bg_color,
                'border': 1,
                'num_format': '0.0%'
            }
        )

        column_formats = {
            'A': ['Ticker', string_format],
            'B': ['Price', dollar_format],
            'C': ['Volume Today', float_format],
            'D': ['Shares Outstanding', float_format],
            'E': [relative_volume, float_format],
            'F': [gap, percent_format],
            'G': [change_from_close, percent_format],
            'H': ['News', string_format],
        }

        for column in column_formats.keys():
            writer.sheets['PMM'].set_column(f'{column}:{column}', 25, column_formats[column][1])
            writer.sheets['PMM'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

        writer.save()

        with open(file_name, 'rb') as f:
            self.send_slack_file(file_name, 'PreMarketMomentum.xlsx', file=io.BytesIO(f.read()))

    def stock_qualifies(self, stock_data):
        if 'quote' not in stock_data:
            return False

        quote = stock_data['quote']

        try:
            self.validate_data(quote)
        except ValueError:
            return False

        # if the latest price is gaping 2%+
        if quote['extendedChangePercent'] >= .02:
            # get some news for the stocks
            data = self.client.stocks.news(quote['symbol'])

            for news in data:
                if time.time() - news['datetime'] < 10800:
                    quote['news'] = news
                    break

            return True

        return False

    @staticmethod
    def validate_data(quote):
        if quote['latestVolume'] is None or 'avgTotalVolume' not in quote or quote['avgTotalVolume'] is None \
                or quote['avgTotalVolume'] is None \
                or quote['extendedChangePercent'] is None \
                or quote['latestVolume'] == 0 \
                or quote['avgTotalVolume'] == 0:
            raise ValueError
