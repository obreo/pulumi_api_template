import pulumi
import pulumi_aws as aws

def api_gateway_http(name: str, lambda_function: str, methods: list, paths: list):
    name = name.lower().strip()
    
    # Create HTTP API
    api = aws.apigatewayv2.Api(f"{name}-api",
        name=name,
        protocol_type="HTTP",
        description=f"HTTP API Gateway for {name}")
    
    # Create Lambda permission
    lambda_permission = aws.lambda_.Permission(f"{name}-api-permission",
        action="lambda:InvokeFunction",
        function=lambda_function.id,
        principal="apigateway.amazonaws.com",
        source_arn=api.execution_arn.apply(lambda arn: f"{arn}/*/*/*"))
    
    # Create integration
    integration = aws.apigatewayv2.Integration(f"{name}-integration",
        api_id=api.id,
        integration_type="AWS_PROXY",
        integration_uri=lambda_function.invoke_arn,
        payload_format_version="2.0")
    
    # Create routes and collect references
    routes = []
    for method in methods:
        for path in paths:
            route = aws.apigatewayv2.Route(f"{method}-{path.replace('/', '-')}",
                api_id=api.id,
                route_key=f"{method} {path}",
                target=integration.id.apply(lambda id: f"integrations/{id}"))
            routes.append(route)
    
    # Create stage with explicit dependency on routes
    stage = aws.apigatewayv2.Stage(f"{name}-stage",
        api_id=api.id,
        name="$default",
        auto_deploy=True,
        opts=pulumi.ResourceOptions(depends_on=routes))  # Critical dependency
    
    # Export outputs
    pulumi.export(f"{name}-api_endpoint", api.api_endpoint)
    return api