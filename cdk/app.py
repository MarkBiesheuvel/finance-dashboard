#!/user/bin/env python3
from os import environ
from importer import Importer
from restapi import RestApi
from website import Website
from aws_cdk import (
    core,
    aws_dynamodb as dynamodb,
)

TICKERS = ['AMZN', 'MSFT', 'GOOGL', 'ORCL', 'BABA']  # Maximum of 5 targets per CloudWatch Event Rule


class FinanceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ticker = dynamodb.Attribute(
            name='Ticker',
            type=dynamodb.AttributeType.STRING,
        )

        date = dynamodb.Attribute(
            name='Date',
            type=dynamodb.AttributeType.STRING,
        )

        table = dynamodb.Table(
            self, 'StockHistory',
            partition_key=ticker,
            sort_key=date,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
        )

        table.add_global_secondary_index(
            index_name='DateTicker-index',
            partition_key=date,
            sort_key=ticker,
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        Importer(self, 'Importer', tickers=TICKERS, table=table)
        restapi = RestApi(self, 'Api', table=table)
        Website(self, 'Website', api=restapi.api)


app = core.App()
stack = FinanceStack(
    app, 'FinanceDashboard',
    env=core.Environment(
        account=environ['CDK_DEFAULT_ACCOUNT'],
        region=environ['CDK_DEFAULT_REGION'],
    )
)
app.synth()
