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
        stock_open = Decimal(str(stock.open))
        stock_high = Decimal(str(stock.high))
        stock_close = Decimal(str(stock.close))
        stock_low = Decimal(str(stock.low))
        stock_volume = Decimal(str(stock.volume))

        item_writer.put_item(
            Item={
                'ticker': ticker,
                'date': stock.date.isoformat(),
                'close': stock_close,
                'high': stock_high,
                'low': stock_low,
                'open': stock_open,
                'volume': stock_volume,
                'updated': stock.updated_at if 'updated_at' in stock else None,
                'changeOverTime': Decimal(str(stock.change_over_time)) if stock.change_over_time is not None else 0,
                'marketChangeOverTime': Decimal(str(stock.market_change_over_time)) if stock.market_change_over_time
                                                                                       is not None else 0,
                'uOpen': Decimal(str(stock.u_open)) if stock.u_open is not None else stock_open,
                'uClose': Decimal(str(stock.u_close)) if stock.u_close is not None else stock_close,
                'uHigh': Decimal(str(stock.u_high)) if stock.u_high is not None else stock_high,
                'uLow': Decimal(str(stock.u_low)) if stock.u_low is not None else stock_low,
                'uVolume': Decimal(str(stock.u_volume)) if stock.u_volume is not None else stock_volume,
                'fOpen': Decimal(str(stock.f_open)) if stock.f_open is not None else stock_open,
                'fClose': Decimal(str(stock.f_close)) if stock.f_close is not None else stock_close,
                'fHigh': Decimal(str(stock.f_high)) if stock.f_high is not None else stock_high,
                'fLow': Decimal(str(stock.f_low)) if stock.f_low is not None else stock_low,
                'fVolume': Decimal(str(stock.f_volume)) if stock.f_volume is not None else stock_volume,
                'change': Decimal(str(stock.change)),
                'changePercent': Decimal(str(stock.change_percent))
            }
        )
