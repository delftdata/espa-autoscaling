FROM rmetzger/flink:1.13.0-reactive-demo
ENV TZ=Europe/Amsterdam
ADD config.yml /opt/config.yml

RUN apt update
RUN apt install -y maven git htop nano iputils-ping wget net-tools
RUN wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.16.1/jmx_prometheus_javaagent-0.16.1.jar
RUN cp jmx_prometheus_javaagent-0.16.1.jar /opt/jmx_prometheus_javaagent.jar

RUN git clone https://github.com/rmetzger/flink-reactive-mode-k8s-demo.git
RUN cd flink-reactive-mode-k8s-demo/reactive-mode-demo-jobs
RUN mvn clean install
