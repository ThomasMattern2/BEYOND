import json
from urllib.parse import parse_qs
import boto3
from botocore.exceptions import ClientError
import bcrypt

dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table("beyond-users")

def email_exists(email):
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(str(email))
        )
        return len(response['Items']) > 0
    except ClientError as e:
        print(f"Error querying DynamoDB for email: {e}")
        return False

def username_exists(username):
    try:
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('username').eq(str(username))
        )
        return len(response['Items']) > 0
    except ClientError as e:
        print(f"Error querying DynamoDB for username: {e}")
        return False
    
def hash_password(password, rounds=5):  # Adjust the rounds as necessary. Too many rounds were resulting in timeouts
    if password:
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode(), salt).decode()
    return None

def create_user(email, username, password, profilePicture, firstName, lastName):
    if not email_exists(email) and not username_exists(username):
        try:
            # Create the user
            table.put_item(
                Item={
                    'email': str(email),
                    'username': str(username),
                    'password': str(password),
                    'profilePicture': str(profilePicture),
                    'firstName': str(firstName),
                    'lastName': str(lastName)
                },
                ConditionExpression='attribute_not_exists(username)'  # Ensure username is unique
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                # This exception is raised when the condition expression fails (username already exists)
                return False
            print(f"Error creating user in DynamoDB: {e}")
    return False


def lambda_handler(event, context):
    http_method = event["requestContext"]["http"]["method"].lower()

    if http_method == "post":  # Assuming you use POST for creating a user
        query = parse_qs(event["rawQueryString"])
        email = query.get('email', [''])[0]
        username = query.get('username', [''])[0]
        password = query.get('password', [''])[0]
        profilePicture = query.get('profilePicture', [''])[0]
        firstName = query.get('firstName', [''])[0]
        lastName = query.get('lastName', [''])[0]
        print(f'{email}  and user {username} and password {password}')
        if not email or not firstName or not lastName:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email, username, first name, or last name parameter is missing'})
            }
        if create_user(email, username, hash_password(password), profilePicture, firstName, lastName):
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
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid HTTP method"})
        }
