"""
Fix Lambda dependencies by ensuring the layer is attached
"""

import boto3
import json

def fix_lambda():
    """Attach the Lambda layer to the function"""
    
    lambda_client = boto3.client('lambda', region_name='ap-south-1')
    
    function_name = 'verigov-dev-verify-sources'
    
    # Get current function config
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        config = response['Configuration']
        
        print(f"Current handler: {config['Handler']}")
        print(f"Current layers: {config.get('Layers', [])}")
        
        # Check if layer exists
        try:
            layers = lambda_client.list_layers()
            verigov_layers = [l for l in layers['Layers'] if 'verigov' in l['LayerName'].lower()]
            
            if verigov_layers:
                layer_arn = verigov_layers[0]['LatestMatchingVersion']['LayerVersionArn']
                print(f"\nFound layer: {layer_arn}")
                
                # Update function to use the layer
                update_response = lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    Layers=[layer_arn]
                )
                
                print(f"\n✅ Updated function to use layer")
                print(f"Function: {update_response['FunctionName']}")
                print(f"Layers: {update_response.get('Layers', [])}")
                
            else:
                print("\n⚠️  No VeriGov layer found. Need to create one.")
                print("Run: scripts/deploy_lambda_layer.py")
                
        except Exception as e:
            print(f"Error checking layers: {e}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    fix_lambda()
