---
title: Segment Geospatial
emoji: 📉
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

Build the docker image:

```bash
# clean any old active containers
docker stop $(docker ps -a -q); docker rm $(docker ps -a -q)

# build the base docker image with the docker aws repository tag
docker build . -f dockerfiles/dockerfile-lambda-gdal-runner --tag 686901913580.dkr.ecr.eu-west-1.amazonaws.com/lambda-gdal-runner

# build the final docker image
docker build . -f dockerfiles/dockerfile-samgeo-api --tag lambda-samgeo-api --progress=plain
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
