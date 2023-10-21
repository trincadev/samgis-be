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

# build the image, use the tag "semgeo"
docker build . --tag semgeo --progress=plain
```

Run the container (keep it on background) and show logs

```bash
docker run  -d --name semgeo -p 7860:7860 semgeo; docker logs -f semgeo
```

Test it with curl:

```bash
curl -X 'POST' \
  'http://localhost:7860/infer_samgeo' \
  -H 'accept: application/json' \
  -d '{}'
```
