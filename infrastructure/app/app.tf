provider aws {
    profile         = "default"
    region          = var.aws_region
}

resource "aws_iam_role_policy" "s3_access" {
    name            = "s3_access"
    role            = aws_iam_role.apgnd_lambda_role.id
    policy          = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Effect": "Allow",
      "Resource": "${aws_s3_bucket.api_configs.arn}",
      "Sid": ""
    }
  ]
}
EOF
}


resource "aws_iam_role" "apgnd_lambda_role" {
    name            = "apgnd_lambda_role"
    assume_role_policy   = <<EOF
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

resource "aws_lambda_function" "apgnd_lambda_func" {
    function_name   = "api_playground_function"
    role            = aws_iam_role.apgnd_lambda_role.arn
    handler         = "src.base.handle"
    runtime         = "python3.8"

    s3_bucket       = var.artifacts_bucket_name
    s3_key          = var.lambda_archive_name 
    environment {
        variables = {
            CONFIG_BUCKET = aws_s3_bucket.api_configs.bucket
        }
    }
}

resource "aws_api_gateway_rest_api" "apgnd_gateway" {
    name            = "apgnd"
    description     = "API Playground"
}

resource "aws_api_gateway_resource" "apgnd_lambda_proxy" {
    rest_api_id     = aws_api_gateway_rest_api.apgnd_gateway.id
    parent_id       = aws_api_gateway_rest_api.apgnd_gateway.root_resource_id
    path_part       = "{proxy+}"
}

resource "aws_api_gateway_method" "apgnd_lambda_proxy" {
    rest_api_id     = aws_api_gateway_rest_api.apgnd_gateway.id
    resource_id     = aws_api_gateway_resource.apgnd_lambda_proxy.id
    http_method     = "ANY"
    authorization   = "NONE"
}

resource "aws_api_gateway_integration" "apgnd_lambda" {
    rest_api_id     = aws_api_gateway_rest_api.apgnd_gateway.id
    resource_id     = aws_api_gateway_resource.apgnd_lambda_proxy.id
    http_method     = aws_api_gateway_method.apgnd_lambda_proxy.http_method

    integration_http_method = "POST"
    type            = "AWS_PROXY"
    uri             = aws_lambda_function.apgnd_lambda_func.invoke_arn
}

resource "aws_api_gateway_deployment" "apgnd_lambda" {
    depends_on = [
        aws_api_gateway_integration.apgnd_lambda
    ]

    rest_api_id     = aws_api_gateway_rest_api.apgnd_gateway.id
    stage_name      = "test"
}

resource "aws_lambda_permission" "apigw" {
    statement_id    = "AllowAPIGatewayInvoke"
    action          = "lambda:InvokeFunction"
    function_name   = aws_lambda_function.apgnd_lambda_func.function_name
    principal       = "apigateway.amazonaws.com"
    source_arn      = "${aws_api_gateway_rest_api.apgnd_gateway.execution_arn}/*/*"
}

output "base_url" {
    value           = aws_api_gateway_deployment.apgnd_lambda.invoke_url
}

resource "aws_s3_bucket" "api_configs" {
    bucket      = var.configs_bucket_name
    acl         = "private"

    tags = {
        Name    = var.configs_bucket_name
    }
}
