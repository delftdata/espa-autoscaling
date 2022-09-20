FROM ubuntu

RUN apt update
RUN apt install -y maven git htop iputils-ping wget net-tools
RUN git clone git@github.com:delftdata/msc-autoscalers-experimental.git
RUN cd msc-autoscalers-experimental/experiments
RUN mvn clean install

WORKDIR /PASAF/experiments