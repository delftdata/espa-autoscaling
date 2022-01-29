FROM ubuntu:21.04

RUN apt update && apt install -y maven git htop iputils-ping wget net-tools && git clone https://github.com/WybeKoper/PASAF.git && cd PASAF/reactive-mode-demo-jobs && mvn clean install

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y vim

CMD ["sleep", "infinity"]