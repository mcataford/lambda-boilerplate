terraform {
  required_version = ">=1.0"

  required_providers {
    aws = "4.29.0"
  }
}

provider "aws" {
  profile = "default"
  region  = var.aws_region
}

