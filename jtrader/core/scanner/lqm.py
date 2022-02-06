#!/usr/bin/env python
# coding: utf-8

import io
from statistics import mean

import pandas as pd
from scipy import stats

from jtrader import chunks
from jtrader.core.provider import IEX

csv_columns = [
    'Ticker',
    'Price',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'Thirty-Day Price Return',
    'Thirty-Day Return Percentile',
    'Five-Day Price Return',
    'Five-Day Return Percentile',
    'LQM Score'
]

time_periods = [
    'Three-Month',
    'One-Month',
    'Thirty-Day',
    'Five-Day'
]


class LowQualityMomentum(IEX):
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
            data = self.client.stocks.batch(symbol_string, ["quote", "stats"])
            for symbol in symbol_string.split(','):
                if symbol not in data or 'quote' not in data[symbol] or data[symbol]['quote']['close'] is None:
                    continue

                series.append(
                    pd.Series(
                        [
                            symbol,
                            data[symbol]['quote']['close'],
                            data[symbol]['stats']['month3ChangePercent'],
                            'N/A',
                            data[symbol]['stats']['month1ChangePercent'],
                            'N/A',
                            data[symbol]['stats']['day30ChangePercent'],
                            'N/A',
                            data[symbol]['stats']['day5ChangePercent'],
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
                df.loc[row, 'LQM Score'] = mean(momentum_percentiles)

        df.sort_values('LQM Score', ascending=False, inplace=True)
        df = df[:50]
        df.reset_index(inplace=True, drop=True)

        file_name = 'LowQualityMomentum.xlsx'

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        df.to_excel(writer, 'LowQualityMomentum', index=False)

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
            'C': ['Three-Month Price Return', percent_format],
            'D': ['Three-Month Return Percentile', percent_format],
            'E': ['One-Month Price Return', percent_format],
            'F': ['One-Month Return Percentile', percent_format],
            'G': ['Thirty-Day Price Return', percent_format],
            'H': ['Thirty-Day Return Percentile', percent_format],
            'I': ['Five-Day Price Return', percent_format],
            'J': ['Five-Day Return Percentile', percent_format],
            'K': ['LQM Score', percent_format]
        }

        for column in column_formats.keys():
            writer.sheets['LowQualityMomentum'].set_column(f'{column}:{column}', 25, column_formats[column][1])
            writer.sheets['LowQualityMomentum'].write(
                f'{column}1',
                column_formats[column][0],
                column_formats[column][1]
            )

        writer.save()

        with open(file_name, 'rb') as f:
            self.send_slack_file(file_name, 'LowQualityMomentum.xlsx', file=io.BytesIO(f.read()))
