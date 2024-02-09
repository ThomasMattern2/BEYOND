terraform {
  required_providers {
    aws = {
      version = ">= 4.0.0"
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
}

# declare any constants here
locals {
  
}

# resource "aws_lambda_function" "name-of-resource" {
#   s3_bucket     = aws_s3_bucket.name.bucket   # or local.s3_bucket_name (initialize this in locals)
#   s3_key        = "name/artifact.zip"
#   role          = aws_iam_role.lambda.arn
#   function_name = "nameoffunction"
#   handler       = "main.lambda_handler"
#   runtime       = "python3.9"
# }

# resource "aws_lambda_function_url" "get_url" {
#   function_name      = aws_lambda_function.name-of-resource.function_name
#   authorization_type = "NONE"

#   cors {
#     allow_credentials = true
#     allow_origins     = [""]
#     allow_methods     = ["get/post"]
#     allow_headers     = ["*"]
#     expose_headers    = [""]
#   }
# }

# # show the function URL after creation
# # output "lambda_url_<add name>" {
# #   value = aws_lambda_function_url.get_url.function_url
# # }

# # create a role for the Lambda function to assume
# resource "aws_iam_role" "lambda" {
#   name               = "iam-for-lambda"
#   assume_role_policy = <<EOF
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Action": "sts:AssumeRole",
#       "Principal": {
#         "Service": "lambda.amazonaws.com"
#       },
#       "Effect": "Allow",
#       "Sid": ""
#     }
#   ]
# }
# EOF
# }

# # create a policy for publishing logs to CloudWatch
# resource "aws_iam_policy" "logs" {
#   name        = "lambda-logging"
#   description = "IAM policy for logging from a lambda"

#   policy = <<EOF
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Action": [
#         "logs:CreateLogGroup",
#         "logs:CreateLogStream",
#         "logs:PutLogEvents",
#         "dynamodb:*"
#       ],
#       "Resource": ["arn:aws:logs:*:*:*", "*"],
#       "Effect": "Allow"
#     }
#   ]
# }
# EOF
# }

# # attach the above policy to the function role
# resource "aws_iam_role_policy_attachment" "lambda_logs" {
#   role       = aws_iam_role.lambda.name
#   policy_arn = aws_iam_policy.logs.arn
# }
