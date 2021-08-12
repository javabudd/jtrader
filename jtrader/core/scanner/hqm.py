#!/usr/bin/env python
# coding: utf-8

import io
from datetime import datetime
from datetime import timedelta
from statistics import mean

import pandas as pd
from cement.core.log import LogInterface
from scipy import stats

from jtrader.core.odm import ODM
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
    def __init__(self, is_sandbox: bool, logger: LogInterface):
        super().__init__(is_sandbox, logger)

        self.odm = ODM()

    def run(self):
        symbols = self.client.symbols()

        series = []
        for stock_symbol in symbols:
            symbol = stock_symbol['symbol']
            one_year_ago = datetime.now() - timedelta(days=365)
            stock_data = self.odm.get_historical_stock_range(symbol, one_year_ago)

            if len(stock_data) <= 1 or 'close' not in stock_data[-1]:
                continue

            df = pd.DataFrame(stock_data)['close'].astype('float')

            one_year_change_percent = df.pct_change(fill_method='ffill').cumsum().iloc[-1]
            six_month_change_percent = df.pct_change(int(len(df) / 2), fill_method='ffill').iloc[-1]
            three_month_change_percent = df.pct_change(int(len(df) / 4), fill_method='ffill').iloc[-1]
            one_month_change_percent = df.pct_change(int(len(df) / 12), fill_method='ffill').iloc[-1]

            series.append(
                [
                    symbol,
                    stock_data[-1]['close'],
                    one_year_change_percent,
                    'N/A',
                    six_month_change_percent,
                    'N/A',
                    three_month_change_percent,
                    'N/A',
                    one_month_change_percent,
                    'N/A',
                    'N/A'
                ],
            )

        df = pd.DataFrame(series, columns=csv_columns)

        for row in df.index:
            momentum_percentiles = []
            for time_period in time_periods:
                change_col = f'{time_period} Price Return'
                percentile_col = f'{time_period} Return Percentile'

                df.loc[row, percentile_col] = stats.percentileofscore(df[change_col], df.loc[row, change_col]) / 100
                momentum_percentiles.append(df.loc[row, percentile_col])
            df.loc[row, 'HQM Score'] = mean(momentum_percentiles)

        df.sort_values('HQM Score', ascending=False, inplace=True)
        df = df[:100]
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
