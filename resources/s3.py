'''
SOURCE:
https://www.pulumi.com/registry/packages/aws/api-docs/s3/bucketv2/
https://www.pulumi.com/registry/packages/aws/api-docs/s3/bucketaclv2/

'''
import pulumi
from pulumi import ResourceOptions
import pulumi_aws as aws
import pulumi_std as std

def bucket(name):
    try:
        name = name.lower().strip()

        # Create Bucket
        bucket_resource = aws.s3.BucketV2(f"{name}",
            bucket=f"{name}",
            force_destroy=True)
        
        ownership_controls = aws.s3.BucketOwnershipControls(f"{name}",
            bucket=bucket_resource.id,
            rule={
                "object_ownership": "BucketOwnerPreferred",
            })
        
        # Configure ACL
        bucket_acl_v2 = aws.s3.BucketAclV2(f"{name}",
            bucket=bucket_resource.id,
            acl="private",
            opts = pulumi.ResourceOptions(depends_on=[ownership_controls]))
        
        # Retrieve the AWS account ID
        account_id = aws.get_caller_identity().account_id

        # Configure Bucket Policy
        # Doc: https://www.pulumi.com/registry/packages/aws/api-docs/iam/getpolicydocument/
        restrict_access = aws.iam.get_policy_document_output(statements=[{
            "principals": [{
                "type": "Service",
                "identifiers": ["cloudfront.amazonaws.com"],
            }],
            "actions": [
                "s3:GetObject"
            ],
            "resources": [
                bucket_resource.arn,
                bucket_resource.arn.apply(lambda arn: f"{arn}/*"),
            ],
            "conditions": [{
                "test": "StringEquals",
                "variable": "aws:SourceAccount",
                "values": [
                    pulumi.Output.from_input(account_id).apply(lambda id: f"{id}")
                ],
            }],
        },
        {
            "principals": [{
                "type": "Service",
                "identifiers": ["lambda.amazonaws.com"],
            }],
            "actions": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket",
            ],
            "resources": [
                bucket_resource.arn.apply(lambda arn: f"{arn}"),
                bucket_resource.arn.apply(lambda arn: f"{arn}/*"),
            ],
            "conditions": [{
                "test": "StringEquals",
                "variable": "aws:SourceAccount",
                "values": [
                    pulumi.Output.from_input(account_id).apply(lambda id: f"{id}")
                ],
            }],
        }])

        assign_bucket_policy = aws.s3.BucketPolicy(f"{name}",
            bucket=bucket_resource.id,
            policy=restrict_access.json)

        # Export the bucket name and arn
        bucket_name = pulumi.export("bucket_name", bucket_resource.bucket)
        bucket_arn = pulumi.export("bucket_arn", bucket_resource.arn)
        return bucket_resource
    except Exception as e:
        return f"ERROR Deploying S3 Bucket: {e}"

def upload_object(bucket, object_path, key_path, DependsOn=None):
    object_file = aws.s3.BucketObject(object_path.replace("/","-").strip().lower(),
    bucket=bucket,
    key=f"{key_path}",
    source=pulumi.FileAsset(f"{object_path}"),
    etag=std.filemd5(input=f"{object_path}").result, opts=ResourceOptions(depends_on=[DependsOn]) if DependsOn else None)