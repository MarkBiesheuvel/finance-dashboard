#!/user/bin/env python3
from aws_cdk import (core,
    aws_s3_assets as assets,
    aws_lambda as lambda_,
    aws_iam as iam,
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

        function = lambda_.Function(self, 'Download',
            runtime=lambda_.Runtime.PYTHON_3_6, # Current version on my machines
            code=lambda_.Code.from_asset('src/download'),
            handler='download.handler',
            role=role,
        )


app = core.App()
stack = FinanceStack(app, 'FinanceDashboard')
app.synth()
