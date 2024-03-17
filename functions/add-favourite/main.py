import json
import boto3
import decimal

# Initialize a DynamoDB resource using the boto3 library.
dynamodb_resource = boto3.resource("dynamodb")
# Connect to the specific DynamoDB table we're working with.
table = dynamodb_resource.Table("beyond-users")

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
        email = query.get('email', [''])

        # Check if all required fields are present.
        if not ngc or not email:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Get the user's current favourites.
        try:
            response = table.get_item(
                Key={"email": email}
            )
            user = response.get("Item", {})
            favourites = user.get("favourites", [])
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Failed to get user: {str(e)}"})
            }

        # Add the new favourite to the user's list.
        try:
            favourites.append(ngc)
            table.update_item(
                Key={"email": email},
                UpdateExpression="SET favourites = :f",
                ExpressionAttributeValues={":f": favourites}
            )
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Failed to update user: {str(e)}"})
            }

        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Favourite added successfully"})
        }
    else:
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }