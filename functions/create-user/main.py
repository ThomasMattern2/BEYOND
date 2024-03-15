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

def hash_password(password, rounds=5):
    """
    Hashes a password using bcrypt with a specified number of rounds.
    
    Parameters:
    - password (str): The password to hash.
    - rounds (int): The number of rounds for the hashing algorithm. Default is 5.
    
    Returns:
    - str: The hashed password.
    """
    if password:
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode(), salt).decode()
    return None

def create_user(email, username, password, firstName, lastName, isGoogle):
    """
    Attempts to create a new user in the DynamoDB table.
    
    Parameters:
    - email (str): The user's email.
    - username (str): The user's username.
    - password (str): The user's hashed password.
    - firstName (str): The user's first name.
    - lastName (str): The user's last name.
    - isGoogle (bool): Whether the account is created via Google.
    
    Returns:
    - bool: True if the user was created successfully, False otherwise.
    """
    if not email_exists(email) and not username_exists(username):
        try:
            table.put_item(
                Item={
                    'email': str(email),
                    'username': str(username),
                    'password': str(password),
                    'firstName': str(firstName),
                    'lastName': str(lastName),
                    'isGoogle': bool(isGoogle)
                },
                ConditionExpression='attribute_not_exists(username)'  # Ensures username does not already exist.
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            print(f"Error creating user in DynamoDB: {e}")
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
        firstName = query.get('firstName', [''])
        lastName = query.get('lastName', [''])
        isGoogle = query.get('isGoogle', [''])
        
        # Check if all required fields are present.
        if not email or not firstName or not lastName or not password or not username or isGoogle is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email, username, password, first name, isGoogle, or last name parameter is missing'})
            }
        # Attempt to create the user and respond accordingly.
        if create_user(email, username, hash_password(password), firstName, lastName, isGoogle):
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'User created successfully'})
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to create user'})
            }
    else:
        # Handle unsupported HTTP methods.
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid HTTP method"})
        }
