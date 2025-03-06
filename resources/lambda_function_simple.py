import pulumi
import pulumi_aws as aws

def lambda_function_py(name):
    # Create an IAM role for the Lambda functions
    name = name.lower().strip()
    lambda_role = aws.iam.Role(f"{name}-lambdaRole",
        assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Effect": "Allow",
                    "Sid": ""
                }
            ]
        }""")

    # Attach a policy to the role
    lambda_role_policy = aws.iam.RolePolicy(f"{name}-lambdaRolePolicy",
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
                    "Action": ["s3:PutObject","s3:GetObject"]
                    "Resource": "*"
                }
            ]
        }""")

    lambda_function = aws.lambda_.Function(name,
        name=name,
        role=lambda_role.arn,
        handler="lambda_code.handler",
        runtime="python3.8",
        code=pulumi.FileArchive("./data/lambda_code.zip")
    )
    pulumi.export(f"{name}-function_name", lambda_function.name)
    pulumi.export(f"{name}-function_arn", lambda_function.arn)
    return lambda_function

