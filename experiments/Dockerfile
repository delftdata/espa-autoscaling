FROM apache/flink:1.14.3

RUN mkdir /opt/flink/plugins/flink-s3-fs-presto && mv /opt/flink/opt/flink-s3-fs-presto-1.14.3.jar /opt/flink/plugins/flink-s3-fs-presto/flink-s3-fs-presto-1.14.3.jar
#  && mv /opt/flink/opt/flink-s3-fs-hadoop-1.14.3.jar /opt/flink/plugins/flink-s3-fs-hadoop

COPY target/flink-examples-1.0-SNAPSHOT-jar-with-dependencies.jar /opt/flink/usrlib/flink-examples-1.0-SNAPSHOT-jar-with-dependencies.jar 