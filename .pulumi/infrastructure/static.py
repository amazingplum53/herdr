import pulumi
import pulumi_aws as aws
import mimetypes
from pathlib import Path
import json

def bucket(stage: str, project_name: str) -> aws.s3.BucketV2:
    # ------------------------------------------------------------------ #
    # 1) Core bucket – ⚠️ NO SSE here
    # ------------------------------------------------------------------ #
    bucket = aws.s3.BucketV2(
        f"{stage}-bucket-{project_name}".replace("_", "-"),
        bucket=f"{stage}-bucket-{project_name}".replace("_", "-"),
        force_destroy=True,
    )

    # ------------------------------------------------------------------ #
    # 2) Server-side encryption (must be a separate resource)
    # ------------------------------------------------------------------ #
    aws.s3.BucketServerSideEncryptionConfigurationV2(
        f"{stage}-bucket-sse-{project_name}".replace("_", "-"),
        bucket=bucket.bucket,
        rules=[
            aws.s3.BucketServerSideEncryptionConfigurationV2RuleArgs(
                apply_server_side_encryption_by_default=
                    aws.s3.BucketServerSideEncryptionConfigurationV2RuleApplyServerSideEncryptionByDefaultArgs(
                        sse_algorithm="AES256"
                    )
            )
        ],
    )

    # ------------------------------------------------------------------ #
    # 4) Public-access settings
    # ------------------------------------------------------------------ #
    aws.s3.BucketPublicAccessBlock(
        f"{stage}-bucket-public-access-block-{project_name}".replace("_", "-"),
        bucket=bucket.bucket,
        block_public_acls=True,
        block_public_policy=True,
        ignore_public_acls=True,
        restrict_public_buckets=True,
    )

    # ------------------------------------------------------------------ #
    # 5) Upload local files – use BucketObjectv2 (lower-case “v”)
    # ------------------------------------------------------------------ #

    root_path = Path(f"/workspace/{project_name}/static/")
    for file_path in root_path.rglob("*"):
        if file_path.is_file():
            rel = file_path.relative_to(root_path).as_posix()
            mime, _ = mimetypes.guess_type(file_path)
            aws.s3.BucketObjectv2(                     # ← fixed name
                f"{stage}-{rel}-{project_name}",
                bucket=bucket.bucket,
                key=rel,
                source=pulumi.FileAsset(str(file_path)),
                content_type=mime or "application/octet-stream",
            )

    return bucket

def cdn(stage: str, project_name: str, bucket: aws.s3.BucketV2, domain_name: str, cert_arn: pulumi.Input[str]) -> aws.cloudfront.Distribution:

    oac = aws.cloudfront.OriginAccessControl(
        f"{stage}-cdn-oac-{project_name}".replace("_", "-"),
        description=f"OAC for {stage}-{project_name}",
        origin_access_control_origin_type="s3",
        signing_behavior="always",
        signing_protocol="sigv4",
    )

    cors_policy = aws.cloudfront.ResponseHeadersPolicy(
        f"{stage}-cdn-cors-policy-{project_name}".replace("_", "-"),
        cors_config=aws.cloudfront.ResponseHeadersPolicyCorsConfigArgs(
            access_control_allow_credentials=False,
            access_control_allow_headers=aws.cloudfront.ResponseHeadersPolicyCorsConfigAccessControlAllowHeadersArgs(
                items=["*"],
            ),
            access_control_allow_methods=aws.cloudfront.ResponseHeadersPolicyCorsConfigAccessControlAllowMethodsArgs(
                items=["GET", "HEAD"],
            ),
            access_control_allow_origins=aws.cloudfront.ResponseHeadersPolicyCorsConfigAccessControlAllowOriginsArgs(
                items=[f"https://{domain_name}"],
            ),
            origin_override=True,
        ),
    )

    # 3) Build the CloudFront Distribution using the us-east-1 provider
    distribution = aws.cloudfront.Distribution(
        f"{stage}-cdnDistribution-{project_name}",
        origins=[aws.cloudfront.DistributionOriginArgs(
            domain_name=bucket.bucket_regional_domain_name,
            origin_id=bucket.arn,
            origin_access_control_id=oac.id,
        )],
        enabled=True,
        default_root_object="index.html",
        default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
            target_origin_id=bucket.arn,
            viewer_protocol_policy="redirect-to-https",
            allowed_methods=["GET", "HEAD"],
            cached_methods=["GET", "HEAD"],
            response_headers_policy_id=cors_policy.id,
            forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                query_string=False,
                cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                    forward="none"
                ),
            ),
        ),
        price_class="PriceClass_100",
        restrictions=aws.cloudfront.DistributionRestrictionsArgs(
            geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                restriction_type="none"
            )
        ),
        aliases=[f"static.{domain_name}"],
        viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
            acm_certificate_arn=cert_arn,
            ssl_support_method="sni-only",
            minimum_protocol_version="TLSv1.2_2021",
        )
    )

    pulumi.export(f"{stage}-cdn_domain_name", distribution.domain_name)
    return distribution


def allow_cloudfront_access(
    stage: str,
    project_name: str,
    bucket: aws.s3.BucketV2,
    distribution: aws.cloudfront.Distribution,
):
    aws.s3.BucketPolicy(
        f"{stage}-bucket-policy-{project_name}".replace("_", "-"),
        bucket=bucket.bucket,
        policy=pulumi.Output.all(bucket.arn, distribution.arn).apply(
            lambda args: json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com"
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"{args[0]}/*",
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceArn": args[1]
                        }
                    },
                }],
            })
        ),
    )
