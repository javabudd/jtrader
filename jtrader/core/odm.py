from datetime import date
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


class ODM:
    def __init__(self):
        dynamodb = boto3.resource('dynamodb')

        self.table = dynamodb.Table('stocks')

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
                'uOpen': Decimal(str(stock['uOpen'])) if stock['uOpen'] is not None else stock_open,
                'uClose': Decimal(str(stock['uClose'])) if stock['uClose'] is not None else stock_close,
                'uHigh': Decimal(str(stock['uHigh'])) if stock['uHigh'] is not None else stock_high,
                'uLow': Decimal(str(stock['uLow'])) if stock['uLow'] is not None else stock_low,
                'uVolume': Decimal(
                    str(stock['uVolume'])
                ) if 'uVolume' in stock and stock['uVolume'] is not None else stock_volume,
                'fOpen': Decimal(str(stock['fOpen'])) if stock['fOpen'] is not None else stock_open,
                'fClose': Decimal(str(stock['fClose'])) if stock['fClose'] is not None else stock_close,
                'fHigh': Decimal(str(stock['fHigh'])) if stock['fHigh'] is not None else stock_high,
                'fLow': Decimal(str(stock['fLow'])) if stock['fLow'] is not None else stock_low,
                'fVolume': Decimal(
                    str(stock['fVolume'])
                ) if 'fVolume' in stock and stock['fVolume'] is not None else stock_volume,
                'change': Decimal(str(stock['change'])),
                'changePercent': Decimal(str(stock['changePercent']))
            }
        )
