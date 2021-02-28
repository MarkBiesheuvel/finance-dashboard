from os import environ
from boto3 import resource
from boto3.dynamodb.conditions import Key
from json import dumps as json_dump
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()

projection_expression = '#d, #o, High, Low, #c'
expression_attributes = {
    '#d': 'Date',
    '#o': 'Open',
    '#c': 'Close'
}

if 'TABLE_NAME' in environ:
    dynamodb = resource('dynamodb')
    table = dynamodb.Table(environ['TABLE_NAME'])
else:
    exit('Environment variable "TABLE_NAME" not set')


@xray_recorder.capture('get_lastest_records')
def get_lastest_records(ticker, days):
    response = table.query(
        Limit=days,
        ScanIndexForward=False,
        ProjectionExpression=projection_expression,
        ExpressionAttributeNames=expression_attributes,
        KeyConditionExpression=Key('Ticker').eq(ticker),
    )

    items = response['Items']
    items.reverse()

    return items


@xray_recorder.capture('get_records_by_daterange')
def get_records_by_daterange(ticker, start, end):
    response = table.query(
        ProjectionExpression=projection_expression,
        ExpressionAttributeNames=expression_attributes,
        KeyConditionExpression=Key('Ticker').eq(ticker) & Key('Date').between(start, end),
    )

    return response['Items']


@xray_recorder.capture('get_dates_from_event')
def get_dates_from_event(event):
    if 'queryStringParameters' not in event:
        return None, None

    qs = event['queryStringParameters']

    if qs is None or \
            'start' not in qs or \
            'end' not in qs:
        return None, None

    return qs['start'], qs['end']


@xray_recorder.capture('handler')
def handler(event, context):
    ticker = event.get('pathParameters', {}).get('ticker', 'AMZN')
    start, end = get_dates_from_event(event)

    if start and end:
        items = get_records_by_daterange(ticker, start, end)
    else:
        items = get_lastest_records(ticker, 60)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'http://[::1]',
        },
        'body': json_dump(items, default=str)
    }
