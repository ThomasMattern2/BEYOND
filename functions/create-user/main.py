import json
from urllib.parse import parse_qs
import boto3
from botocore.exceptions import ClientError

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

def create_user(email, username):
    if not email_exists(email) and not username_exists(username):
        try:
            # Create the user
            table.put_item(
                Item={
                    'email': str(email),
                    'username': str(username)
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
        print(f'{email}  and user {username}')
        if not email or not username:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email or username parameter is missing'})
            }

        if create_user(email, username):
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