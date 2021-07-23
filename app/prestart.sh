#! /usr/bin/env bash
# set env
echo "Setting Environment Variables"
export STATIC_S3_BUCKET_NAME=$(aws ssm get-parameters --names "s3_static_bucket_name" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export STRIPE_SECRET_KEY=$(aws ssm get-parameters --names "stripe_secret_key" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export SLACK_DELIVERY_WEBHOOK_ENDPOINT=$(aws ssm get-parameters --names "slack_delivery_webhook_endpoint" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export STRIPE_WEBHOOK_TOKEN=$(aws ssm get-parameters --names "stripe_webhook_token" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export IOS_SNS_PLATFORM_APPLICATION_ARN=$(aws ssm get-parameters --names "ios_sns_platform_arn" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export ANDROID_SNS_PLATFORM_APPLICATION_ARN=$(aws ssm get-parameters --names "gcm_sns_platform_arn" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export RETOOL_AUTH_KEY=$(aws ssm get-parameters --names "retool_auth_key" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export GOOGLE_MAPS_API_KEY=$(aws ssm get-parameters --names "google_maps_api_key" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export TWILIO_AUTH_TOKEN=$(aws ssm get-parameters --names "twilio_auth_token" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export TWILIO_ACCOUNT_SID=$(aws ssm get-parameters --names "twilio_account_sid" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export REDIS_HOST=$(aws ssm get-parameters --names "redis_host_name" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export MARKETING_TOPIC_ARN=$(aws ssm get-parameters --names "marketing_topic_arn" --with-decryption --query "Parameters[0].Value" | tr -d '"')
if [ -z ${SQLALCHEMY_DATABASE_URI+x} ]; then
export SQLALCHEMY_DATABASE_URI=$(aws ssm get-parameters --names "api_db_database_uri" --with-decryption --query "Parameters[0].Value" | tr -d '"');

fi
# Run migrations
echo "Running Migrations"
alembic upgrade head