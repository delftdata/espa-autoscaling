FROM wurstmeister/kafka:latest

ADD kafka.yml /usr/app/prom-jmx-agent-config.yml

ADD https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.16.1/jmx_prometheus_javaagent-0.16.1.jar  /usr/app/jmx_prometheus_javaagent.jar
