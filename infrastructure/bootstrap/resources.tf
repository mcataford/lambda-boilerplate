resource "aws_s3_bucket" "artifacts" {
    bucket      = var.artifacts_bucket_name

    tags = {
        Name    = var.artifacts_bucket_name
    }
}
