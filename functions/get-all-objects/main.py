import simplejson as json
import boto3

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-objects")

def get_all_objects():
    """
    Queries the DynamoDB table for all objects.
    
    Returns:
    - list: A list of all objects in the table.
    """
    try:
        # Scan the table for all items.
        response = table.scan()
        # Return the list of items with only the desired columns.
        return [{k: v for k, v in item.items() if k not in ["name", "type", "collection"]} for item in response["Items"]]
    except Exception as e:
        return {"error": str(e)}

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
        # Query all objects from the database.
        response = get_all_objects()
        # Check if the response is an error.
        if "error" in response:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response)
            }
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