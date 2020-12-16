#!/user/bin/env python3
from typing import List
from aws_cdk import (
    core,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as events_targets,
    aws_iam as iam,
    aws_lambda as lambda_,
)

IMPORT_JOBS = [
    {
        'market': 'NASDAQ',
        'tickers': ['AMZN', 'GOOGL', 'MSFT'],
        'closing_hour': '21' # GMT
    },
    {
        'market': 'NYSE',
        'tickers': ['BABA', 'IBM', 'ORCL'],
        'closing_hour': '21' # GMT
    }
]


class Importer(core.Construct):

    def __init__(self, scope: core.Construct, id: str, table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role = iam.Role(
            self, 'LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
            ],
        )

        table.grant_write_data(role)

        yfinance_layer = lambda_.LayerVersion(
            self, 'YahooFinance',
            code=lambda_.Code.from_asset('src/yfinance'),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_6,
                lambda_.Runtime.PYTHON_3_7,
                lambda_.Runtime.PYTHON_3_8,
            ]
        )

        function = lambda_.Function(
            self, 'Download',
            runtime=lambda_.Runtime.PYTHON_3_6,  # Current version on my machines
            code=lambda_.Code.from_asset('src/download'),
            handler='download.handler',
            timeout=core.Duration.minutes(1),
            memory_size=1024,
            role=role,
            layers=[yfinance_layer],
            environment={
                'TABLE_NAME': table.table_name
            }
        )

        for job in IMPORT_JOBS:
            target = events_targets.LambdaFunction(
                handler=function,
                event=events.RuleTargetInput.from_object({
                    'market': job['market'],
                    'tickers': job['tickers'],
                    'period': '3d',
                })
            )

            events.Rule(
                self, 'DailyImport{}'.format(job['market']),
                targets=[target],
                schedule=events.Schedule.cron(
                    year='*',
                    month='*',
                    week_day='MON-FRI',  # Only on days which markets are open
                    hour=job['closing_hour'],
                    minute='5',  # 5 minutes after closing
                ),
            )
