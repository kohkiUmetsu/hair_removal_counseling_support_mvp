# Production Environment Configuration

terraform {
  backend "s3" {
    # Configuration loaded from backend.conf
  }
}

module "infrastructure" {
  source = "../../"

  project_name = "counseling-app"
  environment  = "prod"
  aws_region   = "ap-northeast-1"
  
  availability_zones = [
    "ap-northeast-1a",
    "ap-northeast-1c",
    "ap-northeast-1d"
  ]
}