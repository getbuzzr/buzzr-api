# Buzzr API

This repo contains all the code for buzzr api v2

This app is a [FastAPI](https://fastapi.tiangolo.com/) app that is backed by MYSQL, deployed on an elastic beanstalk application cluster

## Develop

1. Set all `.env` variables. There is a `.env.sample`
2. `docker-compose build`
3. `docker-compose up`

## Deploy

All deploys are handled with the CI/CD pipeline

1. CI/CD pipeline generates a docker image
2. Docker image is pushed to ECR
3. Onguard api v2 elastic load balancer is updated with new docker images
