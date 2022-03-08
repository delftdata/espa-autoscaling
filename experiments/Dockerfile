FROM apache/flink:1.14.3


RUN mv /opt/flink/opt/flink-s3-fs-presto-1.14.3.jar /opt/flink/plugins

COPY target/flink-examples-1.0-SNAPSHOT-jar-with-dependencies.jar /opt/flink/usrlib/flink-examples-1.0-SNAPSHOT-jar-with-dependencies.jar 