import json
from urllib.parse import parse_qs
import boto3
from botocore.exceptions import ClientError

dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table("beyond-test")

def exists(email, username):
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(str(email)) &
                                  boto3.dynamodb.conditions.Key('username').eq(str(username))
        )
        return len(response['Items']) > 0
    except ClientError as e:
        print(f"Error querying DynamoDB: {e}")
        return False

def lambda_handler(event, context):
    http_method = event["requestContext"]["http"]["method"].lower()

    if http_method == "delete":
        query = parse_qs(event["rawQueryString"])
        email = query.get('email', [''])[0]
        username = query.get('username', [''])[0]

        if not email or not username:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email or username parameter is missing'})
            }

        if not exists(email, username):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Unauthorized'})
            }

        try:
            response = table.delete_item(
                Key={
                    'email': str(email),
                    'username': str(username)
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'User deleted successfully'})
            }
        except ClientError as e:
            print(f"Error deleting item from DynamoDB: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to delete user'})
            }

    else:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Item not found"})
        }
