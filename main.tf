provider "aws" {
  region = "ap-southeast-3"
}

resource "aws_cognito_user_pool" "main" {
  name = "example_user_pool"
  auto_verified_attributes = ["email"]
  schema {
    attribute_data_type = "String"
    name                = "username"
    mutable             = false
  }

  username_configuration {
    case_sensitive = false
  }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }
}

resource "aws_cognito_user_pool_client" "main" {
  name            = "example_user_pool_client"
  user_pool_id    = aws_cognito_user_pool.main.id
  generate_secret = false
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}

resource "aws_cognito_identity_pool" "main" {
  identity_pool_name               = "example_identity_pool"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.main.id
    provider_name           = "cognito-idp.ap-southeast-3.amazonaws.com/${aws_cognito_user_pool.main.id}"
    server_side_token_check = true
  }
}

resource "aws_iam_role" "authenticated_role" {
  name = "authenticated_role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Federated": "cognito-identity.amazonaws.com"
        },
        "Action": "sts:AssumeRoleWithWebIdentity",
        "Condition": {
          "StringEquals": {
            "cognito-identity.amazonaws.com:aud": "${aws_cognito_identity_pool.main.id}"
          },
          "ForAnyValue:StringLike": {
            "cognito-identity.amazonaws.com:amr": "authenticated"
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "authenticated_policy" {
  name = "authenticated_policy"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:List*"
        ],
        "Resource": "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "authenticated_policy_attachment" {
  role       = aws_iam_role.authenticated_role.name
  policy_arn = aws_iam_policy.authenticated_policy.arn
}

resource "aws_cognito_identity_pool_roles_attachment" "main" {
  identity_pool_id = aws_cognito_identity_pool.main.id

  roles = {
    "authenticated" = aws_iam_role.authenticated_role.arn
  }
}

provider "aws" {
  alias  = "singapore"
  region = "ap-southeast-1"
}

resource "aws_s3_bucket" "example_bucket" {
  provider = aws.singapore
  bucket   = "example-bucket-singapore"
}

output "user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "user_pool_client_id" {
  value = aws_cognito_user_pool_client.main.id
}

output "identity_pool_id" {
  value = aws_cognito_identity_pool.main.id
}

output "s3_bucket_name" {
  value = aws_s3_bucket.example_bucket.bucket
}