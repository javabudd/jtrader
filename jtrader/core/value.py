#!/usr/bin/env python
# coding: utf-8
import io
import statistics

import numpy as np
import pandas as pd
from scipy import stats

from jtrader.core.iex import IEX

stocks = pd.read_csv('files/sp_500_stocks.csv')

csv_columns = [
    'Ticker',
    'Price',
    'Price-to-Earnings Ratio',
    'PE Percentile',
    'Price-to-Book Ratio',
    'PB Percentile',
    'Price-to-Sales Ratio',
    'PS Percentile',
    'EV/EBITDA',
    'EV/EBITDA Percentile',
    'EV/GP',
    'EV/GP Percentile',
    'RV Score'
]

metrics = {
    'Price-to-Earnings Ratio': 'PE Percentile',
    'Price-to-Book Ratio': 'PB Percentile',
    'Price-to-Sales Ratio': 'PS Percentile',
    'EV/EBITDA': 'EV/EBITDA Percentile',
    'EV/GP': 'EV/GP Percentile',
}


class Value(IEX):
    def run(self):
        df = pd.DataFrame(columns=csv_columns)

        symbol_groups = list(self.chunks(stocks['Ticker'], 100))
        symbol_strings = []
        for i in range(0, len(symbol_groups)):
            symbol_strings.append(','.join(symbol_groups[i]))

        for symbol_string in symbol_strings:
            data = self.iex_client.stocks.batch(symbol_string, ["quote", "advanced-stats"])

            for symbol in symbol_string.split(','):
                if data[symbol]['quote']['close'] is None:
                    print('Could not get closing price for %s' % symbol)
                    continue

                pe_ratio = data[symbol]['quote']['peRatio']
                pb_ratio = data[symbol]['advanced-stats']['priceToBook']
                ps_ratio = data[symbol]['advanced-stats']['priceToSales']
                enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
                ebitda = data[symbol]['advanced-stats']['EBITDA']

                try:
                    ev_to_ebitda = enterprise_value / ebitda
                except TypeError:
                    ev_to_ebitda = np.NaN

                gross_profit = data[symbol]['advanced-stats']['grossProfit']

                try:
                    ev_to_gross_profit = enterprise_value / gross_profit
                except TypeError:
                    ev_to_gross_profit = np.NaN

                df = df.append(
                    pd.Series(
                        [
                            symbol,
                            data[symbol]['quote']['latestPrice'],
                            pe_ratio,
                            'N/A',
                            pb_ratio,
                            'N/A',
                            ps_ratio,
                            'N/A',
                            ev_to_ebitda,
                            'N/A',
                            ev_to_gross_profit,
                            'N/A',
                            'N/A'
                        ],
                        index=csv_columns
                    ),
                    ignore_index=True
                )

            for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio', 'Price-to-Sales Ratio', 'EV/EBITDA',
                           'EV/GP']:
                df.fillna(df[column].mean(), inplace=True)

            for metric in metrics.keys():
                for row in df.index:
                    df.loc[row, metrics[metric]] = stats.percentileofscore(df[metric], df.loc[row, metric]) / 100

            for row in df.index:
                value_percentiles = []
                for metric in metrics.keys():
                    value_percentiles.append(df.loc[row, metrics[metric]])

                df.loc[row, 'RV Score'] = statistics.mean(value_percentiles)

        df.sort_values('RV Score', ascending=True, inplace=True)
        df = df[:50]
        df.reset_index(inplace=True, drop=True)

        file_name = 'value_stocks.xlsx'

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        df.to_excel(writer, 'Value', index=False)

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
            'C': ['Price-to-Earnings Ratio', float_format],
            'D': ['PE Ratio', percent_format],
            'E': ['Price-to-Book Ratio', float_format],
            'F': ['PB Ratio', percent_format],
            'G': ['Price-to-Sales Ratio', float_format],
            'H': ['PS Ratio', percent_format],
            'I': ['EV/EBITDA', float_format],
            'J': ['EV/EBITDA Percentile', percent_format],
            'K': ['EV/GP', float_format],
            'L': ['EV/GP Percentile', percent_format],
            'M': ['RV Score', float_format],
        }

        for column in column_formats.keys():
            writer.sheets['Value'].set_column(f'{column}:{column}', 25, column_formats[column][1])
            writer.sheets['Value'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

        writer.save()

        with open(file_name, 'rb') as f:
            self.send_slack_file(file_name, file_name, file=io.BytesIO(f.read()))
