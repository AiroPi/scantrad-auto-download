#!/bin/bash
git pull origin master
docker build -t scantrad-auto-download .
docker rm -f scantrad-auto-download || true
docker run --name scantrad-auto-download -d --restart="always" --env-file=.env scantrad-auto-download
