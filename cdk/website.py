#!/usr/bin/env python3
from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_certificatemanager as acm,
    aws_apigateway as apigateway,
    aws_cloudfront as cloudfront,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
)


class Website(Construct):

    def __init__(self, scope: Construct, id: str, api: apigateway.RestApi, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        stack = Stack.of(self)

        bucket = s3.Bucket(self, 'Storage')

        s3_deployment.BucketDeployment(
            self, 'Deployment',
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
                    default_ttl=Duration.days(1),
                    min_ttl=Duration.days(1),
                    max_ttl=Duration.days(31),
                    is_default_behavior=True,
                )
            ]
        )

        api_origin = cloudfront.SourceConfiguration(
            custom_origin_source=cloudfront.CustomOriginConfig(
                origin_path='/{}'.format(api.deployment_stage.stage_name),
                domain_name='{}.execute-api.{}.{}'.format(
                    api.rest_api_id,
                    stack.region,
                    stack.url_suffix
                ),
            ),
            behaviors=[
                cloudfront.Behavior(
                    default_ttl=Duration.seconds(0),
                    min_ttl=Duration.seconds(0),
                    max_ttl=Duration.seconds(0),
                    path_pattern='/stock/*',
                    forwarded_values={
                        'query_string': True,
                        'query_string_cache_keys': ['start', 'end']
                    }
                )
            ]
        )

        domain_name = 'demo.training'
        subdomain = 'finance.{}'.format(domain_name)

        zone = route53.HostedZone.from_lookup(
            self, 'Zone',
            domain_name=domain_name,
        )

        certificate = acm.DnsValidatedCertificate(
            self, 'Certificate',
            domain_name=subdomain,
            hosted_zone=zone,
            region='us-east-1',
        )

        distribution = cloudfront.CloudFrontWebDistribution(
            self, 'CDN',
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,
            origin_configs=[
                s3_origin,
                api_origin,
            ],
            viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(
                certificate=certificate,
                aliases=[subdomain],
            ),
        )

        target = route53.RecordTarget.from_alias(
            alias_target=route53_targets.CloudFrontTarget(distribution)
        )
        route53.AaaaRecord(
            self, 'DnsRecordIpv6',
            record_name=subdomain,
            target=target,
            zone=zone,
        )
        route53.ARecord(
            self, 'DnsRecordIpv4',
            record_name=subdomain,
            target=target,
            zone=zone,
        )