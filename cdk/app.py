#!/user/bin/env python3
from importer import Importer
from restapi import RestApi
from website import Website
from aws_cdk import (core,
    aws_dynamodb as dynamodb,
)

TICKERS = ['AMZN', 'MSFT', 'GOOGL', 'ORCL', 'BABA'] # Maximum of 5 targets per CloudWatch Event Rule


class FinanceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        table = dynamodb.Table(self, 'StockHistory',
            partition_key=dynamodb.Attribute(
                name='Ticker',
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name='Date',
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        importer = Importer(self, 'Importer', tickers=TICKERS, table=table)
        restapi = RestApi(self, 'Api', table=table)
        website = Website(self, 'Website', api=restapi.api)


app = core.App()
stack = FinanceStack(app, 'FinanceDashboard')
app.synth()
