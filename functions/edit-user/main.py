import json
import boto3
from botocore.exceptions import ClientError
import bcrypt

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-users")

def email_exists(email):
    """
    Checks if an email already exists in the DynamoDB table.
    
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
        print(f"Error querying DynamoDB for email: {e}")
        return False

def username_exists(username):
    """
    Checks if a username already exists in the DynamoDB table.
    
    Parameters:
    - username (str): The username to check in the database.
    
    Returns:
    - bool: True if the username exists, False otherwise.
    """
    try:
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('username').eq(str(username))
        )
        return len(response['Items']) > 0
    except ClientError as e:
        print(f"Error querying DynamoDB for username: {e}")
        return False
    
def is_username_changed(email, username):
    """
    Checks if the username has been changed.
    
    Parameters:
    - email (str): The user's email.
    - username (str): The user's username.
    
    Returns:
    - bool: True if the username has been changed, False otherwise.
    """
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(str(email))
        )
        return response['Items'][0]['username'] != username
    except ClientError as e:
        print(f"Error querying DynamoDB for username: {e}")
        return False

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


def edit_user(email, username, profilePic):
    """
    Attempts to edit a user in the DynamoDB table.
    
    Parameters:
    - email (str): The user's email.
    - username (str): The user's username.
    - profilePic (str): The user's profile picture.
    
    Returns:
    - bool: True if the user was edited successfully, False otherwise.
    """
    try:
        if is_username_changed(email, username) and username_exists(username):
            return False
        # Update the user in the database.
        table.update_item(
            Key={"email": email},
            UpdateExpression="SET username = :username, profilePic = :profilePic",
            ExpressionAttributeValues={
                ":username": username,
                ":profilePic": profilePic
            }
        )       
        return True
    except ClientError as e:
        print(f"Error updating user in DynamoDB: {e}")
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
    print(event)
    http_method = event["requestContext"]["http"]["method"].lower()

    if http_method == "post":  # Handle user creation requests.
        query = json.loads(event["body"])
        
        # Extracting user details from the request body.
        email = query.get('email', [''])
        username = query.get('username', [''])
        password = query.get('password', [''])
        isGoogle = query.get('isGoogle', [''])
        profilePic = query.get('profilePic', [''])
        
        # Check if all required fields are present.
        if not email or not password or not username or isGoogle is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email, username, password, first name, isGoogle, or last name parameter is missing'})
            }
        # Check if the email already exists in the database.
        if not email_exists(email):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Email does not exist'})
            }
        # Check if the user is not a Google user and the password is correct.
        if not isGoogle:
            hashed_password = user_query(email)[0]['password']
            if not authenticate_user(password, hashed_password) or user_query(email)[0]['isGoogle']:
                return {
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Invalid password'})
                }
        # Attempt to create the user and respond accordingly.
        if edit_user(email, username, profilePic):
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'User edited successfully'})
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to edit user'})
            }
    else:
        # Handle unsupported HTTP methods.
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid HTTP method"})
        }
