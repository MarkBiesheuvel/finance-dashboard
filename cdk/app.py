#!/user/bin/env python3
from aws_cdk import (core,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
)


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


app = core.App()
stack = FinanceStack(app, 'FinanceDashboard')
app.synth()
