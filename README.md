# Pulumi Automation API Template for Python
## Deploy your app using Pulumi API with ease

# Overview

Pulumi is one of the leading infrastructure as code (IaC) solutions that uses several programming langauges. One of its primary features is the [Automation API](https://www.pulumi.com/docs/iac/using-pulumi/automation-api/), which allows calling Pulumi API in your code.

This is a quick template, prepared with the primary Pulumi operations that can be used for Pulumi automation API - using Python.

# Features

This template structure is as follows:
```
project_root/
│
├── data/                   # Stores general files
│
├── pulumi_config/          # Pulumi configuration directory
│   ├── config.py           # Environment variables definition
│   └── pulumi_config.py    # Pulumi configuration
│
├── resources/              # CSP resources storage
│
├── app.py                  # Resources called in pulumi_program() function
│
├── .env                    # Pulumi environment details
│
└── requirements.txt        # Pulumi dependencies
```

# Usage

Create the resource required in Resources directory, then import it in the `app.py` and use it in the `pulumi_program` function. 

The current supported Pulumi operations:


###### Command: python app.py [ARGUMENT]

| Argument | Operation | Description |
|----------|-----------|-------------|
| `up`     | Pulumi Up | Create or update resources |
| `destroy`| Pulumi Destroy | Delete all resources |
| `cancel` | Pulumi Cancel | Stop an in-progress update |
| `export` | Pulumi Export | Export stack state |
| `refresh`| Pulumi Refresh | Sync stack state with real-world resources |
| `preview`| Pulumi Preview | Show proposed changes without applying |

# Provided Resources

The followng AWS Rsources are provided and prepared to server multi purpose scenarios:
1. S3: Create bucket and uplaod objects.
2. ECR registry.
3. Lambda: Create a function, upload the code by inserting the code path as list. Supports files, and folders, and Container Image URI.
5. API GATEWAY: Build HTTP or RestAPI. Rest API is designed to build a list of resource paths with custom lambda functions for each using dictionary of inputs.
6. CloudFront Distribution: Supports creating S3 bucket.
7. EventBridge: Supports scheduling a target invocation.

# USEFUL LINKS
1. [Pulumi API for Python](https://www.pulumi.com/docs/reference/pkg/python/pulumi/#module-pulumi.automation)