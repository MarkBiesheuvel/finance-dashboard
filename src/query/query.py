from os import environ
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

if 'TABLE_NAME' in environ:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(environ['TABLE_NAME'])
else:
    exit('Environment variable "TABLE_NAME" not set')


def handler(event, context):

    ticker = event['pathParameters']['ticker']

    response = table.query(
        Limit=60,
        ScanIndexForward=False,
        KeyConditionExpression=Key('Ticker').eq(ticker),
    )
    items = response['Items']
    items.reverse()

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'http://[::1]',
        },
        'body': json.dumps(items, default=str)
    }
