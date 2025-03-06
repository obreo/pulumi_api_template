'''
This script is used to create a pulumi stack, install plugin if needed, and perform stack operations.
The `setting_up_stack` function is used to check if the AWS plugin is installed and install it if needed.
The `handle_stack_operation` function is used to handle different stack operations (up, destroy, cancel, refresh).
The `run_pulumi` function is used to perform the requested operation (up, destroy, cancel, refresh).
This script can be used to automate the deployment of Pulumi stacks and manage the stack operations.
Used with the `cdk/app.py` script to deploy resources using Pulumi.
'''
import logging
from pulumi import automation as auto

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    ...
    
def setting_up_stack(stack, region):
    """Check if AWS plugin is installed and install if needed."""
    try:
        if not stack.workspace.install_plugin("aws", "v6.70.0"):
            print("Installing AWS plugin...")
            stack.workspace.install_plugin("aws", "v6.70.0")

        # Configure AWS region
        if not stack.set_config("aws:region", auto.ConfigValue(value=region)):
            print("Setting up AWS region configuration...")
            stack.set_config("aws:region", auto.ConfigValue(value=region))

        # Refresh stack state
        print("Refreshing Stack...")
        handle_stack_operation(stack, 'refresh')

        return None
    except Exception as e:
        return None


def handle_stack_operation(stack, operation):
    """Handle different stack operations (up, destroy, cancel, refresh)."""
    try:
        logger.info(f"Starting {operation} operation...")
        
        if operation == 'up':
            result = stack.up(on_output=logger.info)
        elif operation == 'destroy':
            result = stack.destroy(on_output=logger.info)
        elif operation == 'cancel':
            result = stack.cancel()
        elif operation == 'refresh':
            result = stack.refresh(on_output=logger.info)
        elif operation == 'export':
            result = stack.export_stack()
            print("Stack state:", result)
        elif operation == 'preview':
            result = stack.preview(on_output=logger.info)
            print("Preview result:", result)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        if result:
            logger.info(f"{operation.capitalize()} operation completed.")
            return None
    except Exception as e:
        logger.error(f"Deployment failed. Check the error above. {e}")
        return None

def run_pulumi(stack,operation=None):
    try:
        # Perform requested operation
        if operation is None:
            operation = 'up'
        if operation in ['up', 'destroy', 'cancel', 'refresh']:
            result = handle_stack_operation(stack, operation)
            if result:
                #logger.info(f"Stack {operation} completed successfully!")
                return result
    except Exception as e:
        logger.error(f"Stack {operation} Terminated!")



if __name__ == "__main__":
    main()