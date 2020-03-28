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
        KeyConditionExpression=Key('Ticker').eq(ticker)
            & Key('Date').between('2020-01-01', '2020-03-31'),
    )
    items = response['Items']

    return {
        'statusCode': 200,
        'body': json.dumps(items, default=str)
    }
