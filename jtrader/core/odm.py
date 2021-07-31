from datetime import date
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


class ODM:
    def __init__(self):
        self.table = boto3.resource('dynamodb').Table('stocks')

    def get_symbols(self):
        today = date.today()

        return self.table.query(KeyConditionExpression=Key('date').eq(today.isoformat()), ScanIndexForward=False)

    def get_historical_stock_day(self, ticker: str, day: str):
        response = self.table.get_item(
            Key={
                'ticker': ticker,
                'date': day
            }
        )

        return response['Item'] if 'Item' in response else None

    def get_historical_stock_range(self, ticker: str, start: date):
        response = self.table.query(
            KeyConditionExpression=Key('ticker').eq(ticker) & Key('date').gte(start.isoformat())
        )

        return response['Items'] if 'Items' in response else []

    @staticmethod
    def put_item(item_writer, ticker, stock):
        stock_open = Decimal(str(stock['open']))
        stock_high = Decimal(str(stock['high']))
        stock_close = Decimal(str(stock['close']))
        stock_low = Decimal(str(stock['low']))
        stock_volume = Decimal(str(stock['volume']))

        u_open = stock_open
        if 'uOpen' in stock and stock['uOpen'] is not None:
            u_open = Decimal(str(stock['uOpen']))

        u_close = stock_close
        if 'uClose' in stock and stock['uClose'] is not None:
            u_close = Decimal(str(stock['uClose']))

        u_high = stock_high
        if 'uHigh' in stock and stock['uHigh'] is not None:
            u_high = Decimal(str(stock['uHigh']))

        u_low = stock_low
        if 'uLow' in stock and stock['uLow'] is not None:
            u_low = Decimal(str(stock['uLow']))

        u_volume = stock_volume
        if 'uVolume' in stock and stock['uVolume'] is not None:
            u_volume = Decimal(str(stock['uVolume']))

        f_open = stock_open
        if 'fOpen' in stock and stock['fOpen'] is not None:
            f_open = Decimal(str(stock['fOpen']))

        f_close = stock_close
        if 'fClose' in stock and stock['fClose'] is not None:
            f_close = Decimal(str(stock['fClose']))

        f_high = stock_high
        if 'fHigh' in stock and stock['fHigh'] is not None:
            f_high = Decimal(str(stock['fHigh']))

        f_low = stock_low
        if 'fLow' in stock and stock['fLow'] is not None:
            f_low = Decimal(str(stock['fLow']))

        f_volume = stock_volume
        if 'fVolume' in stock and stock['fVolume'] is not None:
            f_volume = Decimal(str(stock['fVolume']))

        change = None
        if 'change' in stock and stock['change'] is not None:
            change = Decimal(str(stock['change']))

        change_percent = None
        if 'changePercent' in stock and stock['changePercent'] is not None:
            change_percent = Decimal(str(stock['changePercent']))

        item_writer.put_item(
            Item={
                'ticker': ticker,
                'date': stock['date'],
                'close': stock_close,
                'high': stock_high,
                'low': stock_low,
                'open': stock_open,
                'volume': stock_volume,
                'updated': stock['updatedAt'] if 'updatedAt' in stock else None,
                'changeOverTime':
                    Decimal(str(stock['changeOverTime'])) if stock['changeOverTime'] is not None else 0,
                'marketChangeOverTime': Decimal(
                    str(stock['marketChangeOverTime'])
                ) if stock['marketChangeOverTime'] is not None else 0,
                'uOpen': u_open,
                'uClose': u_close,
                'uHigh': u_high,
                'uLow': u_low,
                'uVolume': u_volume,
                'fOpen': f_open,
                'fClose': f_close,
                'fHigh': f_high,
                'fLow': f_low,
                'fVolume': f_volume,
                'change': change,
                'changePercent': change_percent
            }
        )
