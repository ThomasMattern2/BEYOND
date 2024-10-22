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
      "Resource": [
        "arn:aws:dynamodb:ca-central-1:455720929055:table/beyond-users",
        "arn:aws:dynamodb:ca-central-1:455720929055:table/beyond-objects"
      ]
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

resource "aws_dynamodb_table" "db-objects" {
  name           = "beyond-objects"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

  hash_key = "ngc"

  attribute {
    name = "ngc"
    type = "N"    # type number
  }
  # (More attributes can be added as data is added to the database) 
}

# get-user resources

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

resource "aws_lambda_function" "get-user" {
  role          = aws_iam_role.get-user.arn
  function_name = "get-user"
  handler       = local.lambda_handler
  filename      = "../functions/get-user/dist/get-user.zip"

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
  role          = aws_iam_role.delete-user.arn
  function_name = "delete-user"
  handler       = local.lambda_handler
  filename      = "../functions/delete-user/dist/delete-user.zip"

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
  role          = aws_iam_role.create-user.arn
  function_name = "create-user"
  handler       = local.lambda_handler
  filename      = "../functions/create-user/dist/create-user.zip"

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


# create-object resources

resource "aws_iam_role" "create-object" {
  name                = "iam-for-lambda-create-object"
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

resource "aws_lambda_function" "create-object" {
  role          = aws_iam_role.create-object.arn
  function_name = "create-object"
  handler       = local.lambda_handler
  filename      = "../functions/create-object/dist/create-object.zip"

  runtime = "python3.12"
}

resource "aws_iam_role_policy_attachment" "create-object_logs" {
  role       = aws_iam_role.create-object.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "create-object_dynamo" {
  role       = aws_iam_role.create-object.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "create-object-url" {
  function_name      = aws_lambda_function.create-object.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["POST"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "create-object-lambda_url" {
  value = aws_lambda_function_url.create-object-url.function_url
}

# get-object resources

resource "aws_iam_role" "get-object" {
  name                = "iam-for-lambda-get-object"
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

resource "aws_lambda_function" "get-object" {
  role          = aws_iam_role.get-object.arn
  function_name = "get-object"
  handler       = local.lambda_handler
  filename      = "../functions/get-object/dist/get-object.zip"

  runtime = "python3.12"
}


resource "aws_iam_role_policy_attachment" "get-object_logs" {
  role       = aws_iam_role.get-object.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "get-object_dynamo" {
  role       = aws_iam_role.get-object.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "get-object-url" {
  function_name      = aws_lambda_function.get-object.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["GET"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "get-object_url" {
  value = aws_lambda_function_url.get-object-url.function_url
}

# get-all-objects resources

resource "aws_iam_role" "get-all-objects" {
  name                = "iam-for-lambda-get-all-objects"
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

resource "aws_lambda_function" "get-all-objects" {
  role          = aws_iam_role.get-all-objects.arn
  function_name = "get-all-objects"
  handler       = local.lambda_handler
  filename      = "../functions/get-all-objects/dist/get-all-objects.zip"

  runtime = "python3.12"
}


resource "aws_iam_role_policy_attachment" "get-all-objects_logs" {
  role       = aws_iam_role.get-all-objects.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "get-all-objects_dynamo" {
  role       = aws_iam_role.get-all-objects.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "get-all-objects-url" {
  function_name      = aws_lambda_function.get-all-objects.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["GET"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "get-all-objects_url" {
  value = aws_lambda_function_url.get-all-objects-url.function_url
}

# add-favourite resources
resource "aws_iam_role" "add-favourite" {
  name                = "iam-for-lambda-add-favourite"
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

resource "aws_lambda_function" "add-favourite" {
  role          = aws_iam_role.add-favourite.arn
  function_name = "add-favourite"
  handler       = local.lambda_handler
  filename      = "../functions/add-favourite/dist/add-favourite.zip"

  runtime = "python3.12"
}

resource "aws_iam_role_policy_attachment" "add-favourite_logs" {
  role       = aws_iam_role.add-favourite.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "add-favourite_dynamo" {
  role       = aws_iam_role.add-favourite.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "add-favourite-url" {
  function_name      = aws_lambda_function.add-favourite.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["POST"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "add-favourite-lambda_url" {
  value = aws_lambda_function_url.add-favourite-url.function_url
}

# get-favourites resources

resource "aws_iam_role" "get-favourites" {
  name                = "iam-for-lambda-get-favourites"
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

resource "aws_lambda_function" "get-favourites" {
  role          = aws_iam_role.get-favourites.arn
  function_name = "get-favourites"
  handler       = local.lambda_handler
  filename      = "../functions/get-favourites/dist/get-favourites.zip"

  runtime = "python3.12"
}


resource "aws_iam_role_policy_attachment" "get-favourites_logs" {
  role       = aws_iam_role.get-favourites.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "get-favourites_dynamo" {
  role       = aws_iam_role.get-favourites.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "get-favourites-url" {
  function_name      = aws_lambda_function.get-favourites.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["GET"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "get-favourites_url" {
  value = aws_lambda_function_url.get-favourites-url.function_url
}

# delete-favourite resources
resource "aws_iam_role" "delete-favourite" {
  name                = "iam-for-lambda-delete-favourite"
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

resource "aws_lambda_function" "delete-favourite" {
  role          = aws_iam_role.delete-favourite.arn
  function_name = "delete-favourite"
  handler       = local.lambda_handler
  filename      = "../functions/delete-favourite/dist/delete-favourite.zip"

  runtime = "python3.12"
}

resource "aws_iam_role_policy_attachment" "delete-favourite_logs" {
  role       = aws_iam_role.delete-favourite.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "delete-favourite_dynamo" {
  role       = aws_iam_role.delete-favourite.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "delete-favourite-url" {
  function_name      = aws_lambda_function.delete-favourite.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["DELETE"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "delete-favourite-lambda_url" {
  value = aws_lambda_function_url.delete-favourite-url.function_url
}

# edit-user resources
resource "aws_iam_role" "edit-user" {
  name                = "iam-for-lambda-edit-user"
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

resource "aws_lambda_function" "edit-user" {
  role          = aws_iam_role.edit-user.arn
  function_name = "edit-user"
  handler       = local.lambda_handler
  filename      = "../functions/edit-user/dist/edit-user.zip"

  runtime = "python3.12"
}

resource "aws_iam_role_policy_attachment" "edit-user_logs" {
  role       = aws_iam_role.edit-user.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "edit-user_dynamo" {
  role       = aws_iam_role.edit-user.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "edit-user-url" {
  function_name      = aws_lambda_function.edit-user.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["POST"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "edit-user-lambda_url" {
  value = aws_lambda_function_url.edit-user-url.function_url
}

# delete-object resources

resource "aws_iam_role" "delete-object" {
  name                = "iam-for-lambda-delete-object"
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

resource "aws_lambda_function" "delete-object" {
  role          = aws_iam_role.delete-object.arn
  function_name = "delete-object"
  handler       = local.lambda_handler
  filename      = "../functions/delete-object/dist/delete-object.zip"

  runtime = "python3.12"
}

resource "aws_iam_role_policy_attachment" "delete-object_logs" {
  role       = aws_iam_role.delete-object.name
  policy_arn = aws_iam_policy.logs.arn
}

resource "aws_iam_role_policy_attachment" "delete-object_dynamo" {
  role       = aws_iam_role.delete-object.name
  policy_arn = aws_iam_policy.dynamo.arn
}

resource "aws_lambda_function_url" "delete-object-url" {
  function_name      = aws_lambda_function.delete-object.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["DELETE"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

output "delete-object-lambda_url" {
  value = aws_lambda_function_url.delete-object-url.function_url
}