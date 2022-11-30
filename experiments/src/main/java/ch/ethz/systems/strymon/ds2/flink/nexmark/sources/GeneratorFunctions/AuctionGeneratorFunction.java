package ch.ethz.systems.strymon.ds2.flink.nexmark.sources.GeneratorFunctions;

import org.apache.beam.sdk.nexmark.sources.generator.model.AuctionGenerator;
import org.apache.beam.sdk.nexmark.sources.generator.model.BidGenerator;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.util.Random;

import org.apache.beam.sdk.nexmark.sources.generator.GeneratorConfig;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.core.JsonProcessingException;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;



public class AuctionGeneratorFunction extends GeneratorFunction{

    public AuctionGeneratorFunction(ObjectMapper objectMapper, GeneratorConfig generatorConfig, Producer<String, byte[]> producer, String kafkaTopic, long epochDurationMs) {
        super(objectMapper, generatorConfig, producer, kafkaTopic, epochDurationMs);
    }

    @Override
    public void produceEvent(long eventNumber, Random rnd, long eventTimestampUs) throws JsonProcessingException{
        this.producer.send(new ProducerRecord<String, byte[]>(
                this.kafkaTopic,
                objectMapper.writeValueAsBytes(AuctionGenerator.nextAuction(
                        this.eventsCountSoFar,
                        eventNumber,
                        rnd,
                        eventTimestampUs,
                        this.generatorConfig)
                )
        ));
    }
}
