# Doc: https://www.pulumi.com/registry/packages/aws/api-docs/lambda/function/
# Invoke in CLI: aws lambda invoke --function-name NAME --payload '{}' --profile PROFILENAME --region REGIOM response.json
from pathlib import Path
import pulumi
import pulumi_aws as aws
import os

def lambda_function_py(name: str, runtime: str, handler: str = None, codebase: list = None, env = None, layers: list = None, role = None):
    # Handle codebase archive creation
    if codebase is None:
        # Default codebase if none provided
        codebase_archive = pulumi.FileArchive("./data/lambda_code.zip")
    
    elif any(code[:12].isdigit() for code in codebase):
        codebase_archive = codebase[0]
    else:
        codebase_list = {}
        for i, path in enumerate(codebase, start=1):
            # Check if the path ends with a wildcard (*)
            has_wildcard = path.endswith("*")
            # Remove the wildcard if present
            clean_path = path.rstrip("*").rstrip("/")  # Strip trailing "*" and "/"
            
            # Resolve the cleaned path to an absolute path
            codebase_path = Path(clean_path).resolve()
            
            if codebase_path.is_dir():
                # Include the base folder itself unless the path ends with "*"
                base_folder_name = "" if has_wildcard else codebase_path.name
                
                for file in codebase_path.rglob("*"):  # Recursively find all files
                    if file.is_file():
                        # Compute the relative path from the base directory
                        relative_path = file.relative_to(codebase_path).as_posix()
                        # Prepend the base folder name if not using a wildcard
                        relative_file_path = f"{base_folder_name}/{relative_path}" if base_folder_name else relative_path
                        codebase_list[relative_file_path] = pulumi.FileAsset(str(file))
            elif codebase_path.is_file():
                # For individual files, use their relative path from the base directory
                relative_file_path = codebase_path.name
                codebase_list[relative_file_path] = pulumi.FileAsset(str(codebase_path))
            else:
                print(f"Warning: {codebase_path} does not exist and will be skipped.")
        codebase_archive = pulumi.AssetArchive(codebase_list)

    # Handle environment variables
    env_vars = {}
    if env is not None and isinstance(env, dict):
        env_vars = env
    elif env is not None and isinstance(env, str):
        env_path = env if env.startswith(".") else f"./{env}"
        if os.path.isfile(env_path):
            with open(env_path) as file:
                for line in file:
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
        else:
            print(f"No environment file found at {env_path}")

    # Handle layers
    layers_list = []
    if layers is not None:
        for i, layer in enumerate(layers, start=1):
            if layer.startswith("arn:"):
                layers_list.append(layer)
            else:
                layer_path = layer if layer.startswith(".") else f"./{layer}"
                layer_archive = aws.lambda_.LayerVersion(
                    f"layer_{name}_{i}",
                    layer_name=f"layer_{name}_{i}",
                    code=pulumi.FileArchive(layer_path),
                    compatible_runtimes=[runtime]
                )
                layers_list.append(layer_archive.arn)

    # Create default role if not provided
    if role is None:
        lambda_role = aws.iam.Role(f"{name}-lambdaRole",
            assume_role_policy="""{
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Effect": "Allow",
                    "Sid": ""
                }]
            }"""
        )
        aws.iam.RolePolicy(f"{name}-lambdaRolePolicy",
            role=lambda_role.id,
            policy="""{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "logs:*",
                        "Resource": "arn:aws:logs:*:*:*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["s3:PutObject","s3:GetObject"],
                        "Resource": "*"
                    },
                    {
                    "Effect": "Allow",
                    "Action": [
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage"
                    ],
                    "Resource": "*"
                    }
                ]
            }"""
        )
        role = lambda_role.arn

    # Create Lambda function
    lambda_function = aws.lambda_.Function(name,
        name=name,
        role=role,
        handler = handler or "lambda.handler" if not isinstance(codebase_archive, str) else None,
        runtime=runtime if not isinstance(codebase_archive, str) else None,
        layers=layers_list if not isinstance(codebase_archive, str) else None,
        code = codebase_archive if not isinstance(codebase_archive, str) else None,
        image_uri = codebase_archive if isinstance(codebase_archive, str) and codebase_archive[:12].isdigit() else None,
        environment={"variables": env_vars} if env_vars else None,
        package_type="Image" if isinstance(codebase_archive, str) and codebase_archive[:12].isdigit() else "Zip"
    )
    pulumi.export(f"{name}-function_name", lambda_function.name)
    pulumi.export(f"{name}-function_arn", lambda_function.arn)
    return lambda_function