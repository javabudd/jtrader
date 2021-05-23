#!/usr/bin/env python
# coding: utf-8

from statistics import mean

import pandas as pd
import requests
from scipy import stats

from secrets import IEX_CLOUD_API_TOKEN


def chunks(lst, n):
    for item in range(0, len(lst), n):
        yield lst[item:item + n]


portfolio_value = input('Enter portfolio value: ')

try:
    portfolio_value = float(portfolio_value)
except ValueError as e:
    print('Please enter a valid number')
    exit(0)

stocks = pd.read_csv('sp_500_stocks.csv')

csv_columns = [
    'Ticker',
    'Price',
    'Number of Shares to Buy',
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

df = pd.DataFrame(columns=csv_columns)

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

for symbol_string in symbol_strings:
    api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}' \
              f'&types=quote,stats&token={IEX_CLOUD_API_TOKEN}'
    response = requests.get(api_url)
    data = response.json()

    for symbol in symbol_string.split(','):
        if data[symbol]['quote']['close'] is None:
            continue

        df = df.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']['close'],
                    'N/A',
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
            ),
            ignore_index=True
        )

    position_size = float(portfolio_value) / len(df.index)
    for row in df.index:
        momentum_percentiles = []
        for time_period in time_periods:
            change_col = f'{time_period} Price Return'
            percentile_col = f'{time_period} Return Percentile'

            df.loc[row, percentile_col] = stats.percentileofscore(df[change_col], df.loc[row, change_col]) / 100
            momentum_percentiles.append(df.loc[row, percentile_col])
        df.loc[row, 'HQM Score'] = mean(momentum_percentiles)
        df.loc[row, 'Number of Shares to Buy'] = position_size / df.loc[row, 'Price']

df.sort_values('HQM Score', ascending=False, inplace=True)
df = df[:50]
df.reset_index(inplace=True, drop=True)

writer = pd.ExcelWriter('momentum.xlsx', engine='xlsxwriter')

df.to_excel(writer, 'Momentum', index=False)

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
    'C': ['Number of Shares to Buy', float_format],
    'D': ['One-Year Price Return', percent_format],
    'E': ['One-Year Return Percentile', percent_format],
    'F': ['Six-Month Price Return', percent_format],
    'G': ['Six-Month Return Percentile', percent_format],
    'H': ['Three-Month Price Return', percent_format],
    'I': ['Three-Month Return Percentile', percent_format],
    'J': ['One-Month Price Return', percent_format],
    'K': ['One-Month Return Percentile', percent_format],
    'L': ['HQM Score', percent_format]
}

for column in column_formats.keys():
    writer.sheets['Momentum'].set_column(f'{column}:{column}', 25, column_formats[column][1])
    writer.sheets['Momentum'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

writer.save()
