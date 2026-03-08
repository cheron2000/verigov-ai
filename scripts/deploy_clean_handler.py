"""
Deploy the chosen Lambda handler to AWS Lambda
"""

import boto3
import zipfile
import os
import time


REGION = 'ap-south-1'
FUNCTION_NAME = 'verigov-dev-verify-sources'
LOCAL_FILE = 'lambda/verify_handler_smart_v2.py'
ZIP_INTERNAL_NAME = 'verify_handler_smart_v2.py'
HANDLER_NAME = 'verify_handler_smart_v2.lambda_handler'


def wait_for_lambda_update(lambda_client, function_name, timeout=120):
    """Wait until Lambda update finishes."""
    start = time.time()

    while time.time() - start < timeout:
        response = lambda_client.get_function_configuration(
            FunctionName=function_name
        )
        status = response.get('LastUpdateStatus')
        state = response.get('State')

        print(f"Waiting... State={state}, LastUpdateStatus={status}")

        if state == 'Active' and status == 'Successful':
            return response

        if status == 'Failed':
            raise RuntimeError(
                f"Lambda update failed: {response.get('LastUpdateStatusReason', 'Unknown reason')}"
            )

        time.sleep(5)

    raise TimeoutError("Timed out waiting for Lambda update to complete.")


def deploy():
    """Deploy the smart handler."""
    zip_path = 'lambda_clean_deploy.zip'

    if not os.path.exists(LOCAL_FILE):
        raise FileNotFoundError(f"Handler file not found: {LOCAL_FILE}")

    print("Creating deployment package...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(LOCAL_FILE, ZIP_INTERNAL_NAME)

    print(f"Created {zip_path}")

    lambda_client = boto3.client('lambda', region_name=REGION)

    print(f"\nUploading code to Lambda function: {FUNCTION_NAME}")
    with open(zip_path, 'rb') as f:
        response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=f.read()
        )

    print(f"✅ Code updated: {response['FunctionName']}")
    print(f"   Last Modified: {response['LastModified']}")
    print(f"   Code Size: {response['CodeSize']} bytes")

    print("\nWaiting for code update to finish...")
    wait_for_lambda_update(lambda_client, FUNCTION_NAME)

    print("\nUpdating handler configuration...")
    config_response = lambda_client.update_function_configuration(
        FunctionName=FUNCTION_NAME,
        Handler=HANDLER_NAME
    )

    print(f"✅ Handler set request sent: {config_response['Handler']}")

    print("\nWaiting for configuration update to finish...")
    final_config = wait_for_lambda_update(lambda_client, FUNCTION_NAME)

    print("\nFinal Lambda configuration:")
    print(f"   Handler: {final_config['Handler']}")
    print(f"   State: {final_config['State']}")
    print(f"   LastUpdateStatus: {final_config['LastUpdateStatus']}")

    if os.path.exists(zip_path):
        os.remove(zip_path)

    print("\n✅ Deployment complete!")


if __name__ == '__main__':
    deploy()