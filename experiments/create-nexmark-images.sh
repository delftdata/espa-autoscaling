#!/usr/bin/env bash

docker build -t gsiachamis/flink-nexmark-queries:1.0 .
docker build -f ./Dockerfile.workbench -t gsiachamis/workbench:2.0 .