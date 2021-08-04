# Buzzr API

This repo contains all the code for buzzr api v2

This app is a [FastAPI](https://fastapi.tiangolo.com/) app that is backed by MYSQL, and REDIS deployed on an elastic beanstalk application cluster

## Docker Develop

1. Set all `.envrc` variables. There is a `.env.sample`. You can get the current `.envrc` files from 1password
2. Load AWS access key, secret and session token and replace in `.envrc` file `aws sts assume-role --role-arn "arn:aws:iam::824611589741:role/dev_admin" --role-session-name AWSCLI-Session --profile buzzr --output json --duration-seconds 43200`
3. set `.envrc.docker` from one password also
4. `docker-compose build`
5. `docker-compose up`

## Develop Local

### PreReqs- must have python3.6> installed, docker container for redis/mysql is running

1. Initialize virtual environment `python3 -m venv ENV; source ENV/bin/activate`
2. Install requirements `pip3 install -r requirements.txt`
3. Load AWS access key, secret and session token and replace in `.envrc` file `aws sts assume-role --role-arn "arn:aws:iam::824611589741:role/dev_admin" --role-session-name AWSCLI-Session --profile buzzr --output json --duration-seconds 43200`
4. `source .envrc`
5. run database migrations `cd app;alembic upgrade head;cd ..`
6. `uvicorn main:app`
7. Navigate to `http://127.0.0.1:8000`

## Authenticate

1. Navigate to Cognito dev hosted ui [here](https://dev.auth.getbuzzr.co/login?client_id=79c71u1ff6kg63iaapgvl8k6mm&response_type=code&scope=aws.cognito.signin.user.admin+email+openid&redirect_uri=https://dev.oauth.getbuzzr.co/)
2. Login with social provider and pull auth code found in uri querystring parameter `code`
3.

```
curl -X POST \
  http://dev.auth.getbuzzr.co/oauth2/token \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code&client_id=79c71u1ff6kg63iaapgvl8k6mm&code=YOUR_CODE_HERE&redirect_uri=https%3A%2F%2Fdev.oauth.getbuzzr.co%2F'
```

4. Retreive `access_token` from returned json and copy
5. Add `Authorization: Bearer YOUR_AUTH_TOKEN_HERE` header to api calls

## Deploy

All deploys are handled with the CI/CD pipeline

1. CI/CD pipeline generates a docker image
2. Docker image is pushed to ECR
3. buzz elastic load balancer is updated with new docker images
