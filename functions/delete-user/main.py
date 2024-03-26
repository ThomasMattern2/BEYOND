import json
from urllib.parse import parse_qs
import boto3
from botocore.exceptions import ClientError
import bcrypt
import requests

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-users")

def user_query(email):
    """
    Queries the DynamoDB table for a user with the specified email.
    
    Parameters:
    - email (str): The email to query for.
    
    Returns:
    - list: A list of items (users) matching the query. Empty if no user found.
    """
    try:
        # Scan the table for items with the specified email.
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        return response['Items']
    except ClientError as e:
        print(f"Error querying DynamoDB: {e}")
        return []
    
def authenticate_google_user(access_token):
    """
    Verifies if a user is authenticated with Google using the provided access token.
    
    Parameters:
    - access_token (str): The Google OAuth2 access token.
    
    Returns:
    - bool: True if the user is authenticated with Google, False otherwise.
    """
    # Prepare the authorization header with the access token.
    headers = {"Authorization": f"Bearer {access_token}"}
    # Request to Google's tokeninfo endpoint to validate the access token.
    response = requests.get("https://oauth2.googleapis.com/tokeninfo", headers=headers)
    # If the response status code is 200, the token is valid.
    return response.status_code == 200

def authenticate_user(given_password, stored_password):
    """
    Verifies if the provided password matches the stored hashed password.
    
    Parameters:
    - given_password (str): The password provided by the user.
    - stored_password (str): The hashed password stored in the database.
    
    Returns:
    - bool: True if the passwords match, False otherwise.
    """
    # Use bcrypt to compare the given password with the stored hashed password.
    return bcrypt.checkpw(given_password.encode('utf-8'), stored_password.encode('utf-8'))

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
        
        # Query user info 
        user = user_query(email)

        # Check if user is google user, if so proceed with google auth, otherwise check password
        if user[0].get('isGoogle'):
            # Handle Google authentication.
            access_token = event["headers"]["access_token"]
            if not authenticate_google_user(access_token):
                # Google authentication failed.
                return {
                    "statusCode": 401,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Invalid access token"})
                }
        else:
            password = query.get('password')[0]
            # Handle regular password authentication.
            hashed_password = user[0].get('password')
            if not authenticate_user(password, hashed_password) or user[0].get('isGoogle'):
                # Password does not match or the account is a Google account.
                return {
                    "statusCode": 401,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Incorrect password or Google account required"})
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
