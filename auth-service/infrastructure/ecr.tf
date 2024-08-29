resource "aws_ecr_repository" "my_ecr_repo" {
  name                 = "repo"
  image_tag_mutability = "MUTABLE"
}
