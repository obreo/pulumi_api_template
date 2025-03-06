# Doc: OAC                  - https://www.pulumi.com/registry/packages/aws/api-docs/cloudfront/originaccesscontrol/
# Doc: Distribution         - https://www.pulumi.com/registry/packages/aws/api-docs/cloudfront/distribution/
# Doc: AWS Cache Policy IDs - https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html
import pulumi
import pulumi_aws as aws

def cloudfront_s3(name: str, bucket, path_pattern:str=None, default_root_object: str=None, compress: bool=None, georistriction_locations: list=None, tags: dict=None):
    name = name.lower().replace("_", "-").replace(".", "-").replace("/", "-").strip()
        
    # Create Origin Access Control (OAC)
    oac = aws.cloudfront.OriginAccessControl(f"{name}",
        name=f"{name}",
        description="OAC for S3 origin",
        origin_access_control_origin_type="s3",
        signing_behavior="always",
        signing_protocol="sigv4"
    )
    
    # CloudFront distribution
    s3_origin_id = f"{name}-s3-origin"
    s3_distribution = aws.cloudfront.Distribution(f"{name}",
        enabled=True,
        is_ipv6_enabled=True,
        default_root_object= default_root_object if default_root_object else "index.html",
        origins=[{
            "domain_name": bucket.bucket_regional_domain_name.apply(lambda bucket_domain_name: f"{bucket_domain_name}"),
            "origin_id": s3_origin_id,
            "origin_access_control_id": oac.id.apply(lambda id: f"{id}"),  # Attach OAC
            "custom_origin_config":{
                "http_port": 80,
                "https_port": 443,
                "origin_protocol_policy": "http-only",
                "origin_ssl_protocols": ["TLSv1.2"]
            }
        }],
        default_cache_behavior={
            "cache_policy_id": "b2884449-e4de-46a7-ac36-70bc7f1ddd6d",
            "origin_request_policy_id":"88a5eaf4-2fd4-4709-b370-b4c650ea3fcf",
            "response_headers_policy_id": "60669652-455b-4ae9-85a4-c4c02393f86c",
            "allowed_methods": [
                "GET", "HEAD"
            ],
            "cached_methods": [
                "GET", "HEAD"
            ],
            "target_origin_id": s3_origin_id,
            "viewer_protocol_policy": "redirect-to-https",
            "compress": compress if compress else False
        },
        ordered_cache_behaviors=[
            {
                "allowed_methods": ["GET", "HEAD"],
                "cached_methods": ["GET", "HEAD"],
                "path_pattern": path_pattern if path_pattern else "/*",
                "target_origin_id": s3_origin_id,
                "viewer_protocol_policy": "redirect-to-https",
                "cache_policy_id": "b2884449-e4de-46a7-ac36-70bc7f1ddd6d",
                "compress": compress if compress else False
            }
        ],
        restrictions={
            "geo_restriction": {
                "restriction_type": "whitelist",
                "locations": georistriction_locations if georistriction_locations else [],
            },
        },
        tags=tags if tags else {},
        viewer_certificate={
            "cloudfront_default_certificate": True,
        }
    )
    
    pulumi.export("s3_distribution_id", s3_distribution.id)
    pulumi.export("s3_distribution_domain_name", s3_distribution.domain_name)
    return s3_distribution