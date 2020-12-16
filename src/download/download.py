#!/user/bin/env python3
from boto3 import resource
from boto3.dynamodb.table import BatchWriter
from decimal import Decimal
from os import environ
from typing import List
import yfinance as yf

if 'TABLE_NAME' in environ:
    dynamodb = resource('dynamodb')
    table = dynamodb.Table(environ['TABLE_NAME'])
else:
    exit('Environment variable "TABLE_NAME" not set')


def import_ticker(batch: BatchWriter, ticker: str, period: str):
    stock = yf.Ticker(ticker)
    data = stock.history(
        period=period,
        interval='1d',
    )

    for timestamp, series in data.iterrows():
        batch.put_item(Item={
            'Ticker': ticker,
            'Name': stock.info['shortName'],
            'Date': timestamp.strftime('%Y-%m-%d'),
            'Open': Decimal(str(series['Open'])),
            'Close': Decimal(str(series['Close'])),
            'High': Decimal(str(series['High'])),
            'Low': Decimal(str(series['Low'])),
        })

    print('Imported ticker: {}'.format(ticker))


def import_tickers(tickers : List[str], period: str):
    with table.batch_writer() as batch:
        for ticker in tickers:
            import_ticker(batch, ticker, period)


def handler(event, context):
    market = event.get('market', 'NASDAQ')
    tickers = event.get('tickers', [])
    period = event.get('period', '3d')

    print('Starting import for {}'.format(market))

    import_tickers(tickers, period)

    print('Completed import for {}'.format(market))
