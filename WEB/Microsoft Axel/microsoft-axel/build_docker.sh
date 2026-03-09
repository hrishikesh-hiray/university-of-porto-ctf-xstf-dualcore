#!/bin/bash
docker rm -f microsoft-axel
docker build -t microsoft-axel . &&
  docker run --init --name=microsoft-axel --rm -p 5006:5006 -it microsoft-axel
