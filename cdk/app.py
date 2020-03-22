#!/user/bin/env python3
from aws_cdk import (core,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as events_targets,
    aws_iam as iam,
    aws_lambda as lambda_,
)

tickers = ['AMZN', 'MSFT', 'GOOGL', 'ORCL', 'BABA'] # Maximum of 5 targets per CloudWatch Event Rule


class FinanceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role = iam.Role(self, 'LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
            ],
        )

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
        )

        table.grant_write_data(role)

        function = lambda_.Function(self, 'Download',
            runtime=lambda_.Runtime.PYTHON_3_6, # Current version on my machines
            code=lambda_.Code.from_asset('src/download'),
            handler='download.handler',
            role=role,
            environment={
                'TABLE_NAME': table.table_name
            }
        )

        targets = [
            events_targets.LambdaFunction(
                handler=function,
                event=events.RuleTargetInput.from_object({
                    'ticker': ticker,
                    'period': '3d',
                })
            )
            for ticker in tickers
        ]

        events.Rule(self, 'DailyUpdate',
            targets=targets,
            schedule=events.Schedule.cron(
                year='*',
                month='*',
                week_day='MON-FRI', # Only on days which markets are open
                hour='21', # Closing at NYSE converted from EST to UTC
                minute='5', # 5 minutes after closing
            ),
        )


app = core.App()
stack = FinanceStack(app, 'FinanceDashboard')
app.synth()
