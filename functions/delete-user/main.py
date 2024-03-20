import json
from urllib.parse import parse_qs
import boto3
from botocore.exceptions import ClientError

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-users")

def exists(email):
    """
    Checks if an email exists in the DynamoDB table.
    
    Parameters:
    - email (str): The email to check in the database.
    
    Returns:
    - bool: True if the email exists, False otherwise.
    """
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(str(email))
        )
        return len(response['Items']) > 0
    except ClientError as e:
        print(f"Error querying DynamoDB: {e}")
        return False

def lambda_handler(event, context):
    """
    Handles incoming HTTP requests to the lambda function.
    
    Parameters:
    - event (dict): The event dict containing request parameters and data.
    - context: The runtime information of the Lambda function (unused in this function).
    
    Returns:
    - dict: A response object with statusCode and body.
    """
    http_method = event["requestContext"]["http"]["method"].lower()

    if http_method == "delete":  # Handle delete requests.
        print(event)
        query = parse_qs(event["rawQueryString"])
        email = query.get('email')[0]

        print(query)

        # Check if the email parameter was provided.
        if not email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email parameter is missing'})
            }

        # Verify that the email exists before attempting to delete.
        if not exists(email):  # Corrected to access the first item of the list.
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User not found'})  # Email not found
            }

        try:
            # Attempt to delete the user with the given email.
            response = table.delete_item(
                Key={
                    'email': str(email),
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'User deleted successfully'})
            }
        except ClientError as e:
            print(f"Error deleting item from DynamoDB: {e}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Failed to delete user'})
            }
    else:
        # Respond with error if the HTTP method is not supported.
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid HTTP Method"}) 
        }
