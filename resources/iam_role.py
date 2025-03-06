import pulumi
import json
import pulumi_aws as aws

def iam_role(name: str, service: str, actions: list, resource_arns: list):
    name = name.lower().strip()
    service = service.lower().strip()
    role = aws.iam.Role(name,
        name=name,
        assume_role_policy=pulumi.Output.json_dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Sid": "",
                "Principal": {
                    "Service": f"{service}.amazonaws.com" if "." not in service else service,
                }
            }]
        }))
    policy = aws.iam.RolePolicy(name,
        name=name,
        role=role.id,
        policy=pulumi.Output.json_dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": actions,
                "Effect": "Allow",
                "Resource": resource_arns,
            }]
        }))

    return role
