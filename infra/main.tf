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
  lambda_handler = "main.lambda_handler"
}

# resource "aws_lambda_function" "name-of-resource" {
#   s3_bucket     = aws_s3_bucket.name.bucket   # or local.s3_bucket_name (initialize this in locals)
#   s3_key        = "name/artifact.zip"
#   role          = aws_iam_role.lambda.arn
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

resource "aws_iam_policy" "dynamo" {
  name = "beyond_dynamo"
  description = "Interaction with lambda and dynamo"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:BatchGetItem",
				"dynamodb:GetItem",
				"dynamodb:Query",
				"dynamodb:Scan",
				"dynamodb:BatchWriteItem",
				"dynamodb:PutItem",
				"dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:ca-central-1:455720929055:table/beyond-users"
    }
  ]
}
EOF
}


resource "aws_iam_policy" "logs" {
  name        = "beyond-logging"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role" "get-user" {
  name                = "iam-for-lambda-get-user"
  assume_role_policy  = <<EOF
{
"Version": "2012-10-17",
"Statement": [
  {
    "Action": "sts:AssumeRole",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    },
    "Effect": "Allow",
    "Sid": ""
  }
]
}
EOF
}


resource "aws_dynamodb_table" "db" {
  name           = "beyond-users"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

  hash_key = "email"

  attribute {
    name = "email"
    type = "S"    # type string
  }
  # (More attributes can be added as data is added to the database) 
}

resource "aws_lambda_function" "get-user" {
  # s3_bucket     = aws_s3_bucket.lambda.bucket
  # s3_key        = "beyond-seng401/get-user.zip"
  role          = aws_iam_role.get-user.arn
  function_name = "get-user"
  handler       = local.lambda_handler
  //memory_size   = "128"
  filename      = "../functions/get-user/get-user.zip"
  //source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.12"
}


resource "aws_iam_role_policy_attachment" "get-user_logs" {
  role       = aws_iam_role.get-user.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "get-user_dynamo" {
  role       = aws_iam_role.get-user.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "get-user-url" {
  function_name      = aws_lambda_function.get-user.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["GET"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "get-lambda_url" {
  value = aws_lambda_function_url.get-user-url.function_url
}


# delete user resources

resource "aws_iam_role" "delete-user" {
  name                = "iam-for-lambda-delete-user"
  assume_role_policy  = <<EOF
{
"Version": "2012-10-17",
"Statement": [
  {
    "Action": "sts:AssumeRole",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    },
    "Effect": "Allow",
    "Sid": ""
  }
]
}
EOF
}

resource "aws_lambda_function" "delete-user" {
  # s3_bucket     = aws_s3_bucket.lambda.bucket
  # s3_key        = "beyond-seng401/get-user.zip"
  role          = aws_iam_role.delete-user.arn
  function_name = "delete-user"
  handler       = local.lambda_handler
  //memory_size   = "128"
  filename      = "../functions/delete-user/delete-user.zip"
  //source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.12"
}

resource "aws_iam_role_policy_attachment" "delete-user_logs" {
  role       = aws_iam_role.delete-user.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "delete-user_dynamo" {
  role       = aws_iam_role.delete-user.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "delete-user-url" {
  function_name      = aws_lambda_function.delete-user.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["DELETE"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "delete-lambda_url" {
  value = aws_lambda_function_url.delete-user-url.function_url
}

# create user resources

resource "aws_iam_role" "create-user" {
  name                = "iam-for-lambda-create-user"
  assume_role_policy  = <<EOF
{
"Version": "2012-10-17",
"Statement": [
  {
    "Action": "sts:AssumeRole",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    },
    "Effect": "Allow",
    "Sid": ""
  }
]
}
EOF
}

resource "aws_lambda_function" "create-user" {
  # s3_bucket     = aws_s3_bucket.lambda.bucket
  # s3_key        = "beyond-seng401/create-user.zip"
  role          = aws_iam_role.create-user.arn
  function_name = "create-user"
  handler       = local.lambda_handler
  //memory_size   = "128"
  filename      = "../functions/create-user/create-user.zip"
  //source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.12"
}

resource "aws_iam_role_policy_attachment" "create-user_logs" {
  role       = aws_iam_role.create-user.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "create-user_dynamo" {
  role       = aws_iam_role.create-user.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "create-user-url" {
  function_name      = aws_lambda_function.create-user.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["POST"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "create-lambda_url" {
  value = aws_lambda_function_url.create-user-url.function_url
}
