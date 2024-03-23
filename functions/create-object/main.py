import json
import boto3
import decimal

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-objects")

def exists(ngc):
    """
    Checks if an object exists in the DynamoDB table.
    
    Parameters:
    - ngc (int): The NGC number to check in the database.
    
    Returns:
    - bool: True if the object exists, False otherwise.
    """
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('ngc').eq(ngc)
        )
        print(response)
        return len(response['Items']) > 0
    except Exception as e:
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
        
        # Check if the object already exists.
        if exists(ngc):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Object with this NGC already exists"})
            }
        
        # Attempt to create the object and respond accordingly.
        try:
            print(f"Creating object with NGC: {ngc}")
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
                }
            )
            print("Object created successfully")
            response = {"message": "Object created successfully"}
        except Exception as e:
            response = {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "error": f"Failed to create object: {e}"
            }

        
        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response)
        }
    else:
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }