import boto3
import json
import requests
from urllib.parse import parse_qs

dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table("beyond-test")

def lambda_handler(event, context):
    print("sdfg")