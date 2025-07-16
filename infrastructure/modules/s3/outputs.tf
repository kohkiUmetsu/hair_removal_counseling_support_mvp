output "audio_bucket_name" {
  description = "Name of the S3 bucket for audio files"
  value       = aws_s3_bucket.audio_files.bucket
}

output "audio_bucket_arn" {
  description = "ARN of the S3 bucket for audio files"
  value       = aws_s3_bucket.audio_files.arn
}

output "logs_bucket_name" {
  description = "Name of the S3 bucket for application logs"
  value       = aws_s3_bucket.app_logs.bucket
}

output "logs_bucket_arn" {
  description = "ARN of the S3 bucket for application logs"
  value       = aws_s3_bucket.app_logs.arn
}

output "ecs_s3_role_arn" {
  description = "ARN of the IAM role for ECS tasks to access S3"
  value       = aws_iam_role.ecs_s3_role.arn
}