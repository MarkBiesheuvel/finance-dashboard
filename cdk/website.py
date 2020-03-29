#!/user/bin/env python3
from aws_cdk import (core,
    aws_apigateway as apigateway,
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
)


class Website(core.Construct):

    def __init__(self, scope: core.Construct, id: str, api: apigateway.RestApi, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        stack = core.Stack.of(self)

        bucket = s3.Bucket(self, 'Storage')

        s3_deployment.BucketDeployment(self, 'Deployment',
            sources=[
                s3_deployment.Source.asset('./src/html'),
            ],
            destination_bucket=bucket,
        )

        origin_identity = cloudfront.OriginAccessIdentity(self, 'Identity')

        bucket.grant_read(origin_identity.grant_principal)

        s3_origin = cloudfront.SourceConfiguration(
            s3_origin_source=cloudfront.S3OriginConfig(
                s3_bucket_source=bucket,
                origin_access_identity=origin_identity,
            ),
            behaviors=[
                cloudfront.Behavior(
                    default_ttl=core.Duration.seconds(0),
                    min_ttl=core.Duration.seconds(0),
                    max_ttl=core.Duration.seconds(0),
                    is_default_behavior=True,
                )
            ]
        )

        api_origin = cloudfront.SourceConfiguration(
            origin_path='/{}'.format(api.deployment_stage.stage_name),
            custom_origin_source=cloudfront.CustomOriginConfig(
                domain_name='{}.execute-api.{}.{}'.format(
                    api.rest_api_id,
                    stack.region,
                    stack.url_suffix
                ),
            ),
            behaviors=[
                cloudfront.Behavior(
                    default_ttl=core.Duration.seconds(0),
                    min_ttl=core.Duration.seconds(0),
                    max_ttl=core.Duration.seconds(0),
                    path_pattern='/stock/*',
                    allowed_methods=cloudfront.CloudFrontAllowedMethods.GET_HEAD_OPTIONS,
                )
            ]
        )

        distribution = cloudfront.CloudFrontWebDistribution(self, 'CDN',
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,
            origin_configs=[
                s3_origin,
                api_origin,
            ],
        )
