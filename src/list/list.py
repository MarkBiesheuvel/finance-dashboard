from os import environ
from boto3 import resource
from boto3.dynamodb.conditions import Key
from datetime import timedelta, datetime
from json import dumps as json_dump
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()

if 'INDEX_NAME' in environ:
    index_name = environ['INDEX_NAME']
else:
    exit('Environment variable "INDEX_NAME" not set')

if 'TABLE_NAME' in environ:
    dynamodb = resource('dynamodb')
    table = dynamodb.Table(environ['TABLE_NAME'])
else:
    exit('Environment variable "TABLE_NAME" not set')


@xray_recorder.capture('query')
def query(date: datetime):
    response = table.query(
        IndexName=index_name,
        ProjectionExpression='#n, Ticker',
        ExpressionAttributeNames={
            '#n': 'Name'
        },
        KeyConditionExpression=Key('Date').eq(date.strftime('%Y-%m-%d'))
    )

    return response['Items']


@xray_recorder.capture('list_tickers')
def list_tickers():
    one_day = timedelta(days=1)

    # Try first with yesterday, as today is unlikely to be imported already
    date = datetime.today() - one_day

    items = query(date)

    # Retry until a valid date is found, e.g. markets were not closed
    while len(items) == 0:
        date = date - one_day
        items = list_tickers(date)

    return items


@xray_recorder.capture('handler')
def handler(event, context):
    items = list_tickers()

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'http://[::1]',
        },
        'body': json_dump(items, default=str)
    }
