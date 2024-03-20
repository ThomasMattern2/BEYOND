import simplejson as json
import boto3

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-objects")

def get_object(ngc):
    """
    Queries the DynamoDB table for an object with the specified NGC.
    
    Parameters:
    - NGC (str): The NGC to query for.
    
    Returns:
    - list: A list of items (objects) matching the query. Empty if no object found.
    """
    try:
        # Query the table for items with the specified NGC.
        response = table.query(
            KeyConditionExpression='ngc = :ngc',
            ExpressionAttributeValues={':ngc': int(ngc)}
        )
        if len(response['Items']) == 0:
            return {"error": "No object found with the specified NGC"}
        return response['Items'][0]
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
        query = event["queryStringParameters"]
        print(query)
        ngc = query.get('ngc')
        # Query all objects from the database.
        response = get_object(ngc)
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