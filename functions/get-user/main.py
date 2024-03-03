import boto3
import json
import requests  # Used to make HTTP requests to external services.
from urllib.parse import parse_qs
from botocore.exceptions import ClientError
import bcrypt  # Used for hashing and checking passwords.

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-users")

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
        print(f"Error querying DynamoDB for email: {e}")
        return []

def lambda_handler(event, context):
    """
    Handles incoming HTTP requests to the lambda function.
    
    Parameters:
    - event (dict): The event dict containing request parameters and data.
    - context: The runtime information of the Lambda function (unused in this function).
    
    Returns:
    - dict: A response object with statusCode and body.
    """
    print(event)  # Log the incoming event for debugging.
    http_method = event["requestContext"]["http"]["method"].lower()

    if http_method == "get":
        # Parse the JSON body to extract the email, password, and isGoogle flag.
        query = event["queryStringParameters"]
        print(query)
        email = query.get('email')
        password = query.get('password')
        isgoogle = query.get('isGoogle')

        # Query the user using the provided email.
        response = user_query(email)
        if not response:
            # No user found with the provided email.
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "not a user"})
            }

        if isgoogle.lower() == "true":
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
            # Handle regular password authentication.
            hashed_password = response[0].get('password')
            if not authenticate_user(password, hashed_password) or response[0].get('isGoogle'):
                # Password does not match or the account is a Google account.
                return {
                    "statusCode": 401,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Incorrect password or Google account required"})
                }

        # Authentication successful, return the username.
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"username": response[0].get("username")})
        }
    else:
        # If the request method is not GET, return a 404 error.
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Item not found"})
        }
