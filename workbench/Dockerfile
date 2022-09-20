FROM ubuntu:21.04

RUN apt update && apt install -y maven git htop iputils-ping wget net-tools && git clone git@github.com:delftdata/msc-autoscalers-experimental.git && cd PASAF/experiments && mvn clean install

WORKDIR /PASAF/experiments