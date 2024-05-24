terraform {
  required_version = ">=1.0"

  required_providers {
    aws = "5.51.1"
  }
}

provider "aws" {
  profile = "default"
  region  = var.aws_region
}

