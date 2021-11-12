#!/usr/bin/env python
# coding: utf-8

import io
from statistics import mean

import pandas as pd
from scipy import stats

from jtrader import chunks
from jtrader.core.provider.iex import IEX

csv_columns = [
    'Ticker',
    'Price',
    'One-Year Price Return',
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'HQM Score'
]

time_periods = [
    'One-Year',
    'Six-Month',
    'Three-Month',
    'One-Month'
]


class HighQualityMomentum(IEX):
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
        df = None
        for symbol_string in symbol_strings:
            data = self.client.stocks.batch(symbol_string, ["quote", "stats"])
            for symbol in symbol_string.split(','):
                if symbol not in data or 'quote' not in data[symbol] or data[symbol]['quote'] is None \
                        or data[symbol]['quote']['close'] is None:
                    continue

                series.append(
                    pd.Series(
                        [
                            symbol,
                            data[symbol]['quote']['close'],
                            data[symbol]['stats']['year1ChangePercent'],
                            'N/A',
                            data[symbol]['stats']['month6ChangePercent'],
                            'N/A',
                            data[symbol]['stats']['month3ChangePercent'],
                            'N/A',
                            data[symbol]['stats']['month1ChangePercent'],
                            'N/A',
                            'N/A'
                        ],
                        index=csv_columns
                    )
                )

            df = pd.DataFrame(series, columns=csv_columns)

            for row in df.index:
                momentum_percentiles = []
                for time_period in time_periods:
                    change_col = f'{time_period} Price Return'
                    percentile_col = f'{time_period} Return Percentile'

                    df[change_col].fillna(value=0.0, inplace=True)
                    df.loc[row, percentile_col] = stats.percentileofscore(df[change_col], df.loc[row, change_col]) / 100
                    momentum_percentiles.append(df.loc[row, percentile_col])
                df.loc[row, 'HQM Score'] = mean(momentum_percentiles)

        if df is None:
            return

        df.sort_values('HQM Score', ascending=False, inplace=True)
        df = df[:50]
        df.reset_index(inplace=True, drop=True)

        file_name = 'HighQualityMomentum.xlsx'

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        df.to_excel(writer, 'HighQualityMomentum', index=False)

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
            'C': ['One-Year Price Return', percent_format],
            'D': ['One-Year Return Percentile', percent_format],
            'E': ['Six-Month Price Return', percent_format],
            'F': ['Six-Month Return Percentile', percent_format],
            'G': ['Three-Month Price Return', percent_format],
            'H': ['Three-Month Return Percentile', percent_format],
            'I': ['One-Month Price Return', percent_format],
            'J': ['One-Month Return Percentile', percent_format],
            'K': ['HQM Score', percent_format]
        }

        for column in column_formats.keys():
            writer.sheets['HighQualityMomentum'].set_column(f'{column}:{column}', 25, column_formats[column][1])
            writer.sheets['HighQualityMomentum'].write(
                f'{column}1',
                column_formats[column][0],
                column_formats[column][1]
            )

        writer.save()

        with open(file_name, 'rb') as f:
            self.send_slack_file(file_name, 'HighQualityMomentum.xlsx', file=io.BytesIO(f.read()))
