from os import environ
from decimal import Decimal
import yfinance as yf
import boto3

if 'TABLE_NAME' in environ:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(environ['TABLE_NAME'])
else:
    exit('Environment variable "TABLE_NAME" not set')


def handler(event, context):
    ticker = event.get('ticker', 'AMZN')
    period = event.get('period', '3d')

    stock = yf.Ticker(ticker)

    data = stock.history(
        period=period,
        interval='1d',
    )

    with table.batch_writer() as batch:
        for timestamp, series in data.iterrows():
            batch.put_item(Item={
                'Ticker': ticker,
                'Date': timestamp.strftime('%Y-%m-%d'),
                'Open': Decimal(str(series['Open'])),
                'Close': Decimal(str(series['Close'])),
                'High': Decimal(str(series['High'])),
                'Low': Decimal(str(series['Low'])),
            })

    print('Done {}'.format(ticker))
