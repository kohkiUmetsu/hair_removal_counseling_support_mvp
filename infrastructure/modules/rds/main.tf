# RDS Module

# Random password for database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.project_name}-${var.environment}-db-password"
  description             = "Database password for ${var.project_name} ${var.environment}"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-db-password"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "postgres"
    password = random_password.db_password.result
  })
}


# RDS Parameter Group
resource "aws_db_parameter_group" "main" {
  family = "postgres14"
  name   = "${var.project_name}-${var.environment}-db-params"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-params"
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-db"

  # Engine
  engine         = "postgres"
  engine_version = "14"
  instance_class = var.environment == "prod" ? "db.r5.large" : "db.t3.micro"

  # Storage
  allocated_storage     = var.environment == "prod" ? 100 : 20
  max_allocated_storage = var.environment == "prod" ? 1000 : 100
  storage_type          = "gp2"
  storage_encrypted     = true

  # Database
  db_name  = "counseling_db"
  username = "postgres"
  password = random_password.db_password.result
  port     = 5432

  # Network & Security
  vpc_security_group_ids = [var.database_security_group_id]
  db_subnet_group_name   = var.database_subnet_group_name
  parameter_group_name   = aws_db_parameter_group.main.name

  # Backup & Maintenance
  backup_window           = "03:00-04:00"
  backup_retention_period = var.environment == "prod" ? 7 : 3
  maintenance_window      = "sun:04:00-sun:05:00"

  # Monitoring
  monitoring_interval = var.environment == "prod" ? 60 : 0
  monitoring_role_arn = var.environment == "prod" ? aws_iam_role.rds_enhanced_monitoring[0].arn : null

  # Multi-AZ for production
  multi_az = var.environment == "prod" ? true : false

  # Performance Insights
  performance_insights_enabled = var.environment == "prod" ? true : false

  # Deletion protection
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment != "prod"

  # Tags
  tags = {
    Name = "${var.project_name}-${var.environment}-db"
  }

  lifecycle {
    ignore_changes = [password]
  }
}

# Enhanced Monitoring Role (for production)
resource "aws_iam_role" "rds_enhanced_monitoring" {
  count = var.environment == "prod" ? 1 : 0

  name = "${var.project_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-monitoring-role"
  }
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  count = var.environment == "prod" ? 1 : 0

  role       = aws_iam_role.rds_enhanced_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}