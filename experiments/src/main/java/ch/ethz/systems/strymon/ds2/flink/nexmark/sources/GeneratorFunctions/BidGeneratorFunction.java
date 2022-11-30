package ch.ethz.systems.strymon.ds2.flink.nexmark.sources.GeneratorFunctions;

import org.apache.beam.sdk.nexmark.sources.generator.GeneratorConfig;
import org.apache.beam.sdk.nexmark.sources.generator.model.BidGenerator;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.core.JsonProcessingException;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.util.Random;


public class BidGeneratorFunction extends GeneratorFunction{
    public boolean testRun = false;

    public BidGeneratorFunction(ObjectMapper objectMapper, GeneratorConfig generatorConfig, Producer<String, byte[]> producer, String kafkaTopic, long epochDurationMs) {
        super(objectMapper, generatorConfig, producer, kafkaTopic, epochDurationMs);
    }



    @Override
    public void produceEvent(long eventNumber, Random rnd, long eventTimestampUs) throws JsonProcessingException{
        this.producer.send(new ProducerRecord<String, byte[]>(
                this.kafkaTopic,
                objectMapper.writeValueAsBytes(BidGenerator.nextBid(
                        eventNumber,
                        rnd,
                        eventTimestampUs,
                        this.generatorConfig)
                )
        ));
    }



}
