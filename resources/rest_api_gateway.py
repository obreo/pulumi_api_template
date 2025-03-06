import pulumi
import pulumi_aws as aws
from typing import List, Dict

def main():
    routes = [
    {
        "method": "GET",
        "path": "/media/channel",
        "function": lambda_processor,
    },
    {
        "method": "POST",
        "path": "/media/upload",
        "function": lambda_uploader,
    },
    # Add more endpoints as needed...
]
    api_gateway_rest(PROJECT_NAME, routes)
    
def api_gateway_rest(name: str, endpoints: list, stage="staging", binary_media_types=["*/*"]):
    """
    Create a REST API Gateway that triggers one or more Lambda functions.
    
    Each endpoint in the endpoints list should be a dict with:
      - "method": The HTTP method (e.g., "GET", "POST", etc.)
      - "path": The resource path (e.g., "/media/channel")
      - "function": The corresponding aws.lambda_.Function instance
    """
    name = name.lower().strip()
    
    # Create REST API
    api = aws.apigateway.RestApi(f"{name}-rest-api",
        name=f"{name}",
        description=f"REST API Gateway for {name}",
        endpoint_configuration={
            "types": "REGIONAL"
        },
        binary_media_types=binary_media_types
    )
    
    # Dictionary to track created resources
    resource_map = {"/": api}
    
    # To ensure we only create one Lambda permission per function,
    # track permissions already created.
    lambda_permissions = {}

    # Loop over each endpoint definition
    for i, ep in enumerate(endpoints, start=1):
        method = ep["method"]
        path = ep["path"]
        lambda_function = ep["function"]
        

        # Normalize and split the path into segments
        path_parts = path.strip("/").split("/")
        parent_id = api.root_resource_id
        full_path = ""

        # Create each segment of the path
        for part in path_parts:
            full_path += f"/{part}"
            if full_path not in resource_map:
                resource = aws.apigateway.Resource(f"{name}-resource-{part}",
                    rest_api=api.id,
                    parent_id=parent_id,
                    path_part=part)
                resource_map[full_path] = resource
            parent_id = resource_map[full_path]

        # Create API Gateway method and setting the type
        aws_method = aws.apigateway.Method(f"{name}-method-{method}-{path.replace('/', '-')}",
            rest_api=api.id,
            resource_id=parent_id,
            http_method=method.upper(),
            authorization="NONE")

        # Create API Gateway integration with Lambda
        aws.apigateway.Integration(f"{name}-integration-{method}-{path.replace('/', '-')}",
            rest_api=api.id,
            resource_id=parent_id,
            http_method=aws_method.http_method,
            type="AWS_PROXY",
            integration_http_method="POST",  # AWS Proxy integrations use POST
            uri=lambda_function.invoke_arn,
            opts=pulumi.ResourceOptions(depends_on=[aws_method]))

        # Create Lambda permission if not already created for this function
        if lambda_function.id not in lambda_permissions:
            lambda_permission = aws.lambda_.Permission(f"{name}-api-permission-{i}",
                action="lambda:InvokeFunction",
                function=lambda_function.id,
                principal="apigateway.amazonaws.com",
                source_arn=pulumi.Output.concat(api.execution_arn, "/*"))
            lambda_permissions[lambda_function.id] = lambda_permission

    # Create API Gateway Deployment
    deployment = aws.apigateway.Deployment(f"{name}-deployment",
        rest_api=api.id,
        opts=pulumi.ResourceOptions(depends_on=[api] + list(resource_map.values())))

    # Create the API Gateway Stage
    stage_name = stage  # Avoid variable name conflict
    api_stage = aws.apigateway.Stage(f"{name}-stage-{stage_name}",
        rest_api=api.id,
        deployment=deployment.id,
        stage_name=stage_name)

    # Export API Gateway endpoint
    pulumi.export(f"{name}-api-endpoint", pulumi.Output.format(
        "https://{api_id}.execute-api.{region}.amazonaws.com/{stage}",
        api_id=api.id,
        region=aws.get_region().name,
        stage=api_stage.stage_name))
    
    return api

if __name__ == "__main__":
    main()