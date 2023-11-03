# Segment Geospatial

Build the docker image:

```bash
# clean any old active containers
docker stop $(docker ps -a -q); docker rm $(docker ps -a -q)

# build the base docker image with the docker aws repository tag
docker build . -f dockerfiles/dockerfile-lambda-gdal-runner --tag 686901913580.dkr.ecr.eu-west-1.amazonaws.com/lambda-gdal-runner

# OPTIONAL: to build the lambda-gdal-runner image on a x86 machine use the build arg `RIE="https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie"`:
docker build . -f dockerfiles/dockerfile-lambda-gdal-runner --build-arg RIE="https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie" --tag 686901913580.dkr.ecr.eu-west-1.amazonaws.com/lambda-gdal-runner --progress=plain

# build the final docker image
docker build . -f dockerfiles/dockerfile-lambda-samgeo-api --tag 686901913580.dkr.ecr.eu-west-1.amazonaws.com/lambda-samgeo-api
```

Run the container (keep it on background) and show logs

```bash
docker run  -d --name lambda-samgeo-api -p 8080:8080 lambda-samgeo-api; docker logs -f lambda-samgeo-api
```

Test it with curl:

```bash
curl -X 'POST' \
  'http://localhost:8080/infer_samgeo' \
  -H 'accept: application/json' \
  -d '{}'
```

## Publish the aws lambda
1. Login on aws ECR with the correct aws profile (details on [ECR page](https://eu-west-1.console.aws.amazon.com/ecr/repositories/private/686901913580/surferdtm-prediction-api?region=eu-west-1))
    ```
    aws --profile alessandrotrinca_hotmail_aws_console_ec2_lambda ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 686901913580.dkr.ecr.eu-west-1.amazonaws.com
    ```
2. Build and tag the docker images, then push them:
    ```
    docker push 686901913580.dkr.ecr.eu-west-1.amazonaws.com/lambda-gdal-runner:latest
    docker push 686901913580.dkr.ecr.eu-west-1.amazonaws.com/lambda-samgeo-api:latest
    ```
3. It's possible to publish a new aws lambda version from cmd or from lambda page