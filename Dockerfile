FROM apache/flink:1.14.3

COPY reactive-mode-demo-jobs/target/reactive-mode-demo-jobs-1.0-SNAPSHOT.jar /opt/flink/usrlib/reactive-mode-demo-jobs-1.0-SNAPSHOT.jar