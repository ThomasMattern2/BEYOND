import boto3
import json
import requests
from urllib.parse import parse_qs

dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table("beyond-users")


def lambda_handler(event, context):
    print(event)
    http_method = event["requestContext"]["http"]["method"].lower()
    if http_method == "get":
        query = parse_qs(event["rawQueryString"])
        email = query['email'][0]
        print(email)
        #access_token = event["headers"]["access_token"]
        # verify user is authenticated
        #headers = {"Authorization": f"Bearer {access_token}"}
        #response = requests.get("https://oauth2.googleapis.com/tokeninfo", headers= headers) #if we use google auth
        # if response.status_code != 200:
        #     return {
        #         "statusCode": 401,
        #         "headers": {
        #             "Content-Type": "application/json"
        #         },
        #         "body": json.dumps({
        #             "error": "User is not authenticated"
        #         })
        #     }
        response = table.scan(
            FilterExpression = 'email = :email',
            ExpressionAttributeValues ={':email': email}
        )
        for item in response:
            print(item)
        print(response)

        return {
            "statusCode": 200,
            "headers": {
            "Content-Type": "application/json"
            },
            "body": json.dumps(response['Items'])
            
        }
    else:
        # Return a 404 error if the request was not a get
        return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "error": "Item not found"
                })
            }