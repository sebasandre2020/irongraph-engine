# Terraform Infrastructure Blueprint: IronGraph-Engine

This directory contains the Infrastructure as Code (IaC) configuration for deploying IronGraph-Engine to AWS ECS Fargate, Amazon RDS PostgreSQL, Amazon ElastiCache Redis, and Amazon S3.

## Topology Summary
- **Compute**: AWS ECS Fargate container running FastAPI with LangGraph in private application subnets.
- **Storage**:
  - Amazon S3 bucket with versioning and server-side encryption for adapted workout archives.
  - Amazon RDS PostgreSQL 16 Multi-AZ for lifter profiles, volume landmarks, and relational exercise property graph.
  - Amazon ElastiCache Redis 7 for sub-millisecond lifter session caching and concurrency locks.
- **Security & IAM**: Least-privilege ECS execution and task roles, KMS encryption, and AWS Secrets Manager integration.

## Usage
```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -var="environment=staging" -var="image_tag=v0.1.0"

# Apply
terraform apply -var="environment=staging" -var="image_tag=v0.1.0"
```
