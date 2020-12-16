from os import environ
from boto3 import resource
from boto3.dynamodb.conditions import Key
from json import dumps as json_dump

if 'TABLE_NAME' in environ:
    dynamodb = resource('dynamodb')
    table = dynamodb.Table(environ['TABLE_NAME'])
else:
    exit('Environment variable "TABLE_NAME" not set')


def handler(event, context):
    ticker = event.get('pathParameters', {}).get('ticker', '')
    start = event.get('queryStringParameters', {}).get('start', '')
    end = event.get('queryStringParameters', {}).get('end', '')

    projection_expression = '#d, #o, High, Low, #c'
    expression_attributes = {
        '#d': 'Date',
        '#o': 'Open',
        '#c': 'Close'
    }

    if start and end:
        response = table.query(
            ProjectionExpression=projection_expression,
            ExpressionAttributeNames=expression_attributes,
            KeyConditionExpression=Key('Ticker').eq(ticker) & Key('Date').between(start, end),
        )
        items = response['Items']
    else:
        response = table.query(
            Limit=60,
            ScanIndexForward=False,
            ProjectionExpression=projection_expression,
            ExpressionAttributeNames=expression_attributes,
            KeyConditionExpression=Key('Ticker').eq(ticker),
        )
        items = response['Items']
        items.reverse()

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'http://[::1]',
        },
        'body': json_dump(items, default=str)
    }
