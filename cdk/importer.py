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


class Importer(core.Construct):

    def __init__(self, scope: core.Construct, id: str, tickers: List[str], table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role = iam.Role(
            self, 'LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
            ],
        )

        table.grant_write_data(role)

        function = lambda_.Function(
            self, 'Download',
            runtime=lambda_.Runtime.PYTHON_3_6,  # Current version on my machines
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

        events.Rule(
            self, 'DailyUpdate',
            targets=targets,
            schedule=events.Schedule.cron(
                year='*',
                month='*',
                week_day='MON-FRI',  # Only on days which markets are open
                hour='21',  # Closing at NYSE converted from EST to UTC
                minute='5',  # 5 minutes after closing
            ),
        )
