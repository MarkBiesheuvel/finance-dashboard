#!/user/bin/env python3
from aws_cdk import (core,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
)


class RestApi(core.Construct):

    def __init__(self, scope: core.Construct, id: str, table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role = iam.Role(self, 'LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
            ],
        )

        table.grant_read_data(role)

        function = lambda_.Function(self, 'Query',
            runtime=lambda_.Runtime.PYTHON_3_6, # Current version on my machines
            code=lambda_.Code.from_asset('src/query'),
            handler='query.handler',
            role=role,
            environment={
                'TABLE_NAME': table.table_name
            }
        )

        api = apigateway.RestApi(self, 'StockHistory',
            endpoint_types=[
                apigateway.EndpointType.REGIONAL
            ],
        )

        resource = api.root.add_resource('{ticker}')

        resource.add_cors_preflight(
            allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_credentials=True,
            allow_headers=apigateway.Cors.DEFAULT_HEADERS,
            allow_methods=apigateway.Cors.ALL_METHODS,
        )

        integration = apigateway.LambdaIntegration(
            function,
            proxy=True,
        )

        resource.add_method('GET', integration)
