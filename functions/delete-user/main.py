import boto3
import json
import requests
from urllib.parse import parse_qs

dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table("beyond-test")

# change to email if needed
def exsists(username):
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(str(username))
    )
    # response idk yet
    return len(response['Items']) > 0

def lambda_handler(event, context):
    
    http_method = event["requestContext"]["http"]["method"].lower()
    
    if http_method == "delete":

        query = parse_qs(event["rawQueryString"])
        username = query['username'][0]
        print(username) # format of ['username'] change to username
        if not exsists(username):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Unauthorized'})
            }
        try:    
            response = table.delete_item(
                Key={
                    # any id other id or email in db
                    'username': username,
                }
            )

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'User deleted successfully'})
            }
        except Exception as e:
            print(e)
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to delete user'})
            }
            
    else:
        # Return a 404 error if the request was not delete
        return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "error": "Item not found"
                })
            }