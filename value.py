#!/usr/bin/env python
# coding: utf-8
import statistics

import numpy as np
import pandas as pd
import requests
from scipy import stats

import utils
from secrets import IEX_CLOUD_API_TOKEN

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

df = pd.DataFrame(columns=csv_columns)

symbol_groups = list(utils.chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

for symbol_string in symbol_strings:
    api_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}' \
              f'&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}'
    response = requests.get(api_url)
    data = response.json()

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
                    'N/A',
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

    for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio', 'Price-to-Sales Ratio', 'EV/EBITDA', 'EV/GP']:
        df.fillna(df[column].mean(), inplace=True)

    for metric in metrics.keys():
        for row in df.index:
            df.loc[row, metrics[metric]] = stats.percentileofscore(df[metric], df.loc[row, metric]) / 100

    position_size = float(portfolio_value) / len(df.index)
    for row in df.index:
        value_percentiles = []
        for metric in metrics.keys():
            value_percentiles.append(df.loc[row, metrics[metric]])

        df.loc[row, 'RV Score'] = statistics.mean(value_percentiles)
        df.loc[row, 'Number of Shares to Buy'] = position_size / df.loc[row, 'Price']

df.sort_values('RV Score', ascending=True, inplace=True)
df = df[:50]
df.reset_index(inplace=True, drop=True)

writer = pd.ExcelWriter('value_stocks.xlsx', engine='xlsxwriter')

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
    'C': ['Number of Shares to Buy', float_format],
    'D': ['Price-to-Earnings Ratio', float_format],
    'E': ['PE Ratio', percent_format],
    'F': ['Price-to-Book Ratio', float_format],
    'G': ['PB Ratio', percent_format],
    'H': ['Price-to-Sales Ratio', float_format],
    'I': ['PS Ratio', percent_format],
    'J': ['EV/EBITDA', float_format],
    'K': ['EV/EBITDA Percentile', percent_format],
    'L': ['EV/GP', float_format],
    'M': ['EV/GP Percentile', percent_format],
    'N': ['RV Score', float_format],
}

for column in column_formats.keys():
    writer.sheets['Value'].set_column(f'{column}:{column}', 25, column_formats[column][1])
    writer.sheets['Value'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

writer.save()
