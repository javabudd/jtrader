from datetime import date
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


class ODM:
    def __init__(self):
        dynamodb = boto3.resource('dynamodb')

        self.table = dynamodb.Table('stocks')

    def get_historical_stock_day(self, ticker: str, day):
        response = self.table.get_item(
            Key={
                'ticker': ticker,
                'date': day.isoformat()
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
        item_writer.put_item(
            Item={
                'ticker': ticker,
                'date': stock.date.isoformat(),
                'close': Decimal(str(stock.close)),
                'high': Decimal(str(stock.high)),
                'low': Decimal(str(stock.low)),
                'open': Decimal(str(stock.open)),
                'volume': Decimal(str(stock.volume)),
                'updated': stock.updated_at if 'updated_at' in stock else None,
                'changeOverTime': Decimal(str(stock.change_over_time)),
                'marketChangeOverTime': Decimal(str(stock.market_change_over_time)),
                'uOpen': Decimal(str(stock.u_open)),
                'uClose': Decimal(str(stock.u_close)),
                'uHigh': Decimal(str(stock.u_high)),
                'uLow': Decimal(str(stock.u_low)),
                'uVolume': Decimal(str(stock.u_volume)) if stock.u_volume is not None else 0,
                'fOpen': Decimal(str(stock.f_open)),
                'fClose': Decimal(str(stock.f_close)),
                'fHigh': Decimal(str(stock.f_high)),
                'fLow': Decimal(str(stock.f_low)),
                'fVolume': Decimal(str(stock.f_volume)) if stock.f_volume is not None else 0,
                'change': Decimal(str(stock.change)),
                'changePercent': Decimal(str(stock.change_percent))
            }
        )
