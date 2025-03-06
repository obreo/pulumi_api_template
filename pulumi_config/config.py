'''
Environment variables are used to store sensitive information such as access keys, secret keys, and other configuration information.
The `load_dotenv` function is used to load the environment variables from the `.env` file.
The `os` module is used to access the environment variables.
These environment variables are then used to configure the Pulumi program and create resources.
'''
from dotenv import load_dotenv
import os

load_dotenv()

PULUMI_ACCESS_TOKEN = os.getenv("PULUMI_ACCESS_TOKEN")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("REGION")
PROJECT_NAME = os.getenv("PROJECT_NAME")
STACK_NAME = os.getenv("STACK_NAME")

