# resource "aws_iam_role" "lambda_iam_role" {
#   name = "lambda_iam_role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "sts:AssumeRole"
#         Effect = "Allow"
#         Principal = {
#           Service = "lambda.amazonaws.com"
#         }
#       }
#     ]
#   })
# }

# resource "aws_iam_policy" "lambda_s3_policy" {
#   name        = "lambda-s3-access"
#   description = "IAM policy for Lambda to access S3 bucket"
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "s3:GetObject",
#           "s3:ListBucket"
#         ],
#         Effect = "Allow"
#         Resource = [
#           aws_s3_bucket.hyper_bucket.arn,
#           "${aws_s3_bucket.hyper_bucket.arn}/*"
#         ]
#       }
#     ]
#   })

# }

# resource "aws_iam_role_policy_attachment" "lambda_role_attachment" {
#   policy_arn = aws_iam_policy.lambda_s3_policy.arn
#   role       = aws_iam_role.lambda_iam_role.name
# }
