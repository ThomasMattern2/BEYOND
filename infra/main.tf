resource "aws_lambda_function" "name" {
  s3_bucket     = aws_s3_bucket.name.bucket
  s3_key        = "name/artifact.zip"
  role          = aws_iam_role.lambda.arn
  function_name = "nameoffunction"
  handler       = "main.lambda_handler"
  runtime       = "python3.9"
}

resource "aws_lambda_function_url" "get_url" {
  function_name      = "nameoffunction
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = [""]
    allow_methods     = ["get/post"]
    allow_headers     = ["*"]
    expose_headers    = [""]
  }
}