#!/user/bin/env python3
from aws_cdk import (
    core,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
)


class RestApi(core.Construct):

    def __init__(self, scope: core.Construct, id: str, table: dynamodb.Table, index_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        role = iam.Role(
            self, 'LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
            ],
        )

        table.grant_read_data(role)

        xray = lambda_.LayerVersion(
            self, 'Xray',
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_6,
                lambda_.Runtime.PYTHON_3_7,
                lambda_.Runtime.PYTHON_3_8,
            ],
            code=lambda_.Code.from_asset('src/xray'),
        )

        list_function = lambda_.Function(
            self, 'List',
            runtime=lambda_.Runtime.PYTHON_3_7,  # Current version on my machines
            code=lambda_.Code.from_asset('src/list'),
            handler='list.handler',
            role=role,
            tracing=lambda_.Tracing.ACTIVE,
            layers=[
                xray,
            ],
            environment={
                'TABLE_NAME': table.table_name,
                'INDEX_NAME': index_name,
            }
        )

        list_version = lambda_.Version(
            self, 'ListVersion',
            lambda_=list_function,
            removal_policy=core.RemovalPolicy.DESTROY,
            provisioned_concurrent_executions=1,  # Avoid cold starts
        )

        query_function = lambda_.Function(
            self, 'Query',
            runtime=lambda_.Runtime.PYTHON_3_7,  # Current version on my machines
            code=lambda_.Code.from_asset('src/query'),
            handler='query.handler',
            role=role,
            tracing=lambda_.Tracing.ACTIVE,
            layers=[
                xray,
            ],
            environment={
                'TABLE_NAME': table.table_name
            }
        )

        query_version = lambda_.Version(
            self, 'QueryVersion',
            lambda_=query_function,
            removal_policy=core.RemovalPolicy.DESTROY,
            provisioned_concurrent_executions=1,  # Avoid cold starts
        )

        api = apigateway.RestApi(
            self, 'StockHistory',
            endpoint_types=[
                apigateway.EndpointType.REGIONAL
            ],
            cloud_watch_role=True,
            deploy_options=apigateway.StageOptions(
                logging_level=apigateway.MethodLoggingLevel.ERROR,
                metrics_enabled=True,
                tracing_enabled=True,
            ),
        )

        stock_root_resource = api.root.add_resource('stock')
        stock_id_resource = stock_root_resource.add_resource('{ticker}')

        stock_root_resource.add_method(
            http_method='GET',
            integration=apigateway.LambdaIntegration(
                list_version,
                proxy=True,
            ),
        )

        stock_id_resource.add_method(
            http_method='GET',
            integration=apigateway.LambdaIntegration(
                query_version,
                proxy=True,
            ),
            request_parameters={
                'method.request.querystring.start': False,
                'method.request.querystring.end': False,
            },
        )

        self.api = api
