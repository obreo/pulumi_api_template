'''
This is the main entry point for the Pulumi program.
Resources are defined in this file.
Start the program by running the command: `python app.py`
'''
from pulumi import automation as auto
from pulumi_config import *
import pulumi
from dotenv import load_dotenv
import os
import sys
import logging
import traceback
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )
logger = logging.getLogger(__name__)

# Suppress noisy logs
logging.getLogger("grpc").setLevel(logging.CRITICAL)  # Add this line
os.environ["PULUMI_LOGLEVEL"] = "WARN" 

# Load environment variables
load_dotenv(".env")

# RESOURCES
from resources.s3 import bucket, upload_object
from resources.ecr import ecr
from resources.lambda_function import lambda_function_py
from resources.rest_api_gateway import api_gateway_rest
from resources.event_bridge import scheduler
from resources.iam_role import iam_role
from resources.cloudfront_s3 import cloudfront_s3



'''___________________________________________________________________________________________________________________'''
def pulumi_program():
    """Define the Pulumi infrastructure program."""
    try:
    # RESOURCE: S3    
        # Bucket
        bucket_resource = bucket(PROJECT_NAME)
        # Upload Object
        Object = bucket_resource.apply(lambda bucket: upload_object(bucket=bucket,object_path="",key_path=""))
        
    # RESOURCE: ECR
        ecr_repo = ecr(name=PROJECT_NAME, mutable=True, scan_on_push=False)

    # RESOURCE: LAMBDA FUNCTION
        # Processor
        lambda_example = lambda_function_py(name=f"{PROJECT_NAME}", runtime="python3.13",handler="lambda_code.lambda_handler", codebase=["data/lambda_code.py"])

    # RESOURCE: API GATEWAY
        endpoints = [
            {
                "method": "GET",
                "path": "/path/",
                "function": lambda_example,
            }
            # You can add more endpoints here...
        ]
        processor_api = api_gateway_rest(PROJECT_NAME, endpoints)
                
    # RESOURCE: EVENT BRIDGE
        # IAM Role
        role = iam_role(name=f"{PROJECT_NAME}", service="scheduler.amazonaws.com", actions=["lambda:InvokeFunction"], resource_arns=[lambda_example.arn])
        
        # Cron Scheduler
        expression = "cron(0 0 * * ? *)"

        # Event Target
        lambda_target = pulumi.Output.all(lambda_example.arn, role.arn).apply(lambda outputs: {"arn": outputs[0], "role_arn": outputs[1]})
        
        # Event Rule
        schedule_event = scheduler(name=PROJECT_NAME, schedule_expression=expression, target=lambda_target)

    # RESOURCE: CLOUDFRONT
        cloudfront = pulumi.Output.all(bucket_resource).apply(lambda bucket: cloudfront_s3(name=PROJECT_NAME, bucket=bucket[0], path_pattern="media/*"))

        return "Resources Deployed Successfully"
    except Exception as e:
        logger.error(f"Error in Pulumi program. Diagnosis: \n{str(e)}\nTraceback: {traceback.format_exc()}")
        return None

'''___________________________________________________________________________________________________________________'''
def main():
    parser = argparse.ArgumentParser(description="Pulumi automation API template to run operations on Pulumi stacks")
    parser.add_argument('operation', nargs='?', choices=['up', 'refresh', 'cancel', 'export', 'preview'], default='up', help="Pulumi operation to perform (default: 'up')")
    args = parser.parse_args()
    try:
        # Create or Select Stack
        stack = auto.create_or_select_stack(
            stack_name=STACK_NAME,
            project_name=PROJECT_NAME,
            program=pulumi_program,
            work_dir=os.getcwd()
        )

        # Check and install plugin if needed
        setting_up_stack(stack,REGION)

        # Start pulumi by default using 'up' and Get operation from command line args; 
        #operation = 'up'
        #if len(sys.argv) > 1:
        #    operation = sys.argv[1].lower()
        # Get operation from command line args
        operation = args.operation.lower()
        
        run_pulumi(stack, operation)


    except Exception as e:
        logger.error(f"Error: {str(e)}")
        traceback.print_exc()  # Prints the full traceback
        sys.exit(1)
        return None

    
if __name__ == "__main__":
    main()