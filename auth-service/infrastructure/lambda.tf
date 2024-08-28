# resource "aws_lambda_function" "lambda_function" {
#   function_name = "auth-function"
#   # filename         = data.archive_file.dist.output_path
#   s3_bucket        = aws_s3_bucket.hyper_bucket.bucket
#   s3_key           = aws_s3_object.lambda_zip.key
#   source_code_hash = data.archive_file.dist.output_base64sha256
#   # image_uri     = var.image_uri
#   # package_type  = "Image"
#   role    = aws_iam_role.lambda_iam_role.arn
#   handler = "main.handler"
#   runtime = "python3.10"
#   timeout = 60
#   environment {
#     variables = {
#       for line in split("\n", file("../auth-service/.env")) :
#       split("=", line)[0] => split("=", line)[1]
#       if length(trimspace(line)) > 0 && !startswith(trimspace(line), "#")
#     }
#   }
# }

# resource "aws_lambda_function_url" "lambda_function_url" {
#   function_name      = aws_lambda_function.lambda_function.function_name
#   authorization_type = "NONE"
#   # authorization_type = "AWS_IAM"
# }

# output "lambda_function_url" {
#   value = aws_lambda_function_url.lambda_function_url.function_url
# }
