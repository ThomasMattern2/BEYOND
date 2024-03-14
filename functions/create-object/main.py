import json
import boto3
import decimal

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-objects")

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
    print(http_method)

    if http_method == "post":
        # Query all objects from the database.
        query = json.loads(event["body"])
        
        # Extracting user details from the request body.
        ngc = int(query.get('ngc', ['']))
        name = query.get('name', [''])
        type = query.get('type', [''])
        constellation = query.get('constellation', [''])
        ra = decimal.Decimal(query.get('ra', '0'))
        dec = decimal.Decimal(query.get('dec', '0'))
        magnitude = decimal.Decimal(query.get('magnitude', '0'))
        collection = query.get('collection', [''])

        # Check if all required fields are present.
        if not ngc or not name or not type or not constellation or not ra or not dec or not magnitude or not collection:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Attempt to create the object and respond accordingly.
        try:
            table.put_item(
                Item={
                    "ngc": ngc,
                    "name": name,
                    "type": type,
                    "constellation": constellation,
                    "ra": ra,
                    "dec": dec,
                    "magnitude": magnitude,
                    "collection": collection
                },
                ConditionExpression='attribute_not_exists(ngc)'  # Ensures ngc does not already exist.
            )
            response = {"message": "Object created successfully"}
        except dynamodb_resource.meta.client.exceptions.ConditionalCheckFailedException:
            response = {"error": "Object with this NGC already exists"}
        except Exception as e:
            response = {"error": f"Failed to create object: {e}"}

        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response)
        }
    else:
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }