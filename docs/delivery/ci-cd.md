# CI/CD Pipeline Blueprint: IronGraph-Engine

## 1. Pipeline Principles
IronGraph-Engine enforces a strict, multi-stage **Continuous Integration and Continuous Delivery (CI/CD)** pipeline using GitHub Actions:
- **Fast Feedback**: Linting and schema validation run in parallel under 60 seconds.
- **Contract Parity**: OpenAPI 3.1 specifications and JSON schemas are validated against test fixtures on every pull request.
- **Biomechanical Rule Testing**: Automated unit tests assert that zero contraindicated exercises are ever suggested under simulated injury conditions.
- **Zero-Downtime Deployment**: ECS Fargate executes rolling blue/green deployments, verifying `/health/live` before draining older tasks.

## 2. Pipeline Execution Stages

```mermaid
flowchart LR
  PR[GitHub Pull Request] --> Lint[Stage 1: Lint & Format Check (Ruff)]
  PR --> Contract[Stage 2: Schema & Contract Validator]
  PR --> Test[Stage 3: PyTest Biomechanics & Rule Tests]
  
  Lint & Contract & Test --> Merge[Merge to Main]
  
  Merge --> Build[Stage 4: Docker Multi-Stage Build]
  Build --> Scan[Stage 5: Trivy Security Scan]
  Scan --> Push[Stage 6: Push to AWS ECR]
  Push --> Deploy[Stage 7: Terraform Apply & ECS Deploy]
  Deploy --> Smoke[Stage 8: Production Smoke Tests]
```
