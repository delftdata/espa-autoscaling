FROM ubuntu:21.04

RUN apt update && apt install -y maven git htop iputils-ping wget net-tools && git clone https://github.com/WybeKoper/PASAF.git && cd PASAF/experiments && mvn clean install

WORKDIR /PASAF/experiments