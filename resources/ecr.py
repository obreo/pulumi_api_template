# Doc: https://www.pulumi.com/registry/packages/aws/api-docs/ecr/repository/
# Push Command: (Get-ECRLoginCommand -ProfileName PROFILENAME -Region REGION).Password | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.REGION.amazonaws.com
import pulumi
import pulumi_aws as aws

def ecr(name:str, mutable:bool=True, scan_on_push:bool=False):
    name = name.lower().strip()
    try:
        ecr = aws.ecr.Repository(f"{name}",
            name=name,
            image_tag_mutability="MUTABLE" if mutable else "IMMUTABLE",
            image_scanning_configuration={
                "scan_on_push": True if scan_on_push else False,
            })
        
        pulumi.export("ecr_uri", ecr.repository_url.apply(lambda uri: f"{uri}:latest"))
        return ecr
    except Exception as e:
        raise None