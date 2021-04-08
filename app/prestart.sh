#! /usr/bin/env bash
# set env
echo "Setting Environment Variables"
export STATIC_S3_BUCKET_NAME=$(aws ssm get-parameters --names "s3_static_bucket_name" --with-decryption --query "Parameters[0].Value" | tr -d '"')
export STRIPE_SECRET_KEY=$(aws ssm get-parameters --names "stripe_secret_key" --with-decryption --query "Parameters[0].Value" | tr -d '"')
if [ -z ${SQLALCHEMY_DATABASE_URI+x} ]; then
export SQLALCHEMY_DATABASE_URI=$(aws ssm get-parameters --names "api_db_database_uri" --with-decryption --query "Parameters[0].Value" | tr -d '"');
fi
# Run migrations
echo "Running Migrations"
alembic upgrade head