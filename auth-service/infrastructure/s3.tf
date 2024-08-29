# resource "aws_s3_bucket" "hyper_bucket" {
#   bucket = "hyper-hyper-bucket"
# }

# data "archive_file" "dist" {
#   source_dir  = "../auth-service/src"
#   output_path = "dist.zip"
#   type        = "zip"
# }

# resource "aws_s3_object" "lambda_zip" {
#   bucket = aws_s3_bucket.hyper_bucket.bucket
#   source = data.archive_file.dist.output_path
#   key    = "dist.zip"
# }
