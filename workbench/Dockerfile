# this is our first build stage, it will not persist in the final image
FROM ubuntu as intermediate

# install git
RUN apt-get update
RUN apt-get install -y git


# Set ssh key for access to private repository
ARG SSH_PRIVATE_KEY
RUN mkdir /root/.ssh
RUN echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Clone repository
RUN git clone git@github.com:delftdata/msc-autoscalers-experimental.git

# Create real image
FROM ubuntu
COPY --from=intermediate /msc-autoscalers-experimental /msc-autoscalers-experimental

RUN apt update
RUN apt install -y maven git htop iputils-ping wget net-tools
RUN cd msc-autoscalers-experimental/experiments && mvn clean install

WORKDIR /msc-autoscalers-experimental/experiments