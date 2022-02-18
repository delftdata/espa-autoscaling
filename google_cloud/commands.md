kubectl expose deployment hello-world --type=LoadBalancer --name=my-service
exposing service to internet

constant mode:
mvn exec:java -Dexec.mainClass="ch.ethz.systems.strymon.ds2.flink.nexmark.sources.BidSourceFunctionGeneratorKafka" -Dexec.args="--mode 0 --rate 100000"