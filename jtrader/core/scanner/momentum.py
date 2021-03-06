#!/usr/bin/env python
# coding: utf-8

import io
import time

import pandas as pd

from jtrader import chunks
from jtrader.core.provider import IEX

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


class Momentum(IEX):
    def run(self):
        stocks = self.client.symbols()

        stock_chunks = chunks(stocks, 100)
        symbol_strings = []
        for chunk in stock_chunks:
            symbols = []
            for stock in chunk:
                symbols.append(stock['symbol'])

            symbol_strings.append(','.join(symbols))

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
                                data[symbol]['quote']['latestPrice'],
                                data[symbol]['quote']['latestVolume'],
                                data[symbol]['stats']['sharesOutstanding'],
                                1 - (data[symbol]['quote']['avgTotalVolume'] / data[symbol]['quote']['latestVolume']),
                                data[symbol]['quote']['changePercent'],
                                1 - (data[symbol]['quote']['previousClose'] / data[symbol]['quote']['latestPrice']),
                                news
                            ],
                            index=csv_columns
                        )
                    )

        df = pd.DataFrame(series, columns=csv_columns)

        if df.empty:
            self.logger.info('No stocks on PMM radar')

            return

        df.sort_values([gap, relative_volume, change_from_close], ascending=False, inplace=True)
        df.reset_index(inplace=True, drop=True)

        file_name = 'MarketMomentum.xlsx'

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
            self.send_slack_file(file_name, 'MarketMomentum.xlsx', file=io.BytesIO(f.read()))

    def stock_qualifies(self, stock_data):
        if 'quote' not in stock_data:
            return False

        quote = stock_data['quote']

        if 'avgTotalVolume' not in quote or 'latestVolume' not in quote or 'changePercent' not in quote:
            return False

        if quote['changePercent'] is None or quote['latestVolume'] is None or quote['avgTotalVolume'] is None:
            return False

        # if the latest price is gaping 10%+
        if quote['changePercent'] >= .1:
            # @TODO this needs tweaking depending on time of day?
            if quote['latestVolume'] != 0 and quote['avgTotalVolume'] != 0 \
                    and (quote['latestVolume'] - quote['avgTotalVolume']) / quote['avgTotalVolume'] >= .1:
                # get some news for the stocks
                data = self.client.stocks.news(quote['symbol'])

                for news in data:
                    if time.time() - news['datetime'] < 10800:
                        quote['news'] = news
                        break

                return True

        return False
