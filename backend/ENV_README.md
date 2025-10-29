# Environment files for Cost Guardian Backend
# ================================================

# .env files are used for local development and contain sensitive information
# They should NEVER be committed to version control

# Files created:
# - env.example     : Template with all possible environment variables
# - env.local       : Local development configuration
# - env.production  : Production configuration template

# Usage:
# 1. Copy env.example to .env for local development
# 2. Fill in your actual values in .env
# 3. Use env.production as reference for AWS Lambda environment variables

# Security Notes:
# - Add .env to .gitignore
# - Use AWS Secrets Manager for production secrets
# - Use IAM roles for AWS credentials in Lambda
# - Never hardcode secrets in code

# Environment Variable Categories:
# - AWS Configuration
# - Database (PostgreSQL)
# - Vector Database (Pinecone/Weaviate)
# - LLM (Google Gemini - Primary)
#   * GEMINI_API_KEY: Your Google Gemini API key
#   * GEMINI_MODEL: Model name (default: gemini-1.5-flash)
# - LLM (OpenAI/Anthropic) - Optional fallback
# - Lambda Function Names
# - SNS/SQS Configuration
# - API Configuration
# - Monitoring & Logging
# - Data Collection Settings
# - RAG Configuration
# - Cost Optimization Thresholds
# - Email/Notification Settings
# - Security Configuration
# - Feature Flags
