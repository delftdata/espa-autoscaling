package ch.ethz.systems.strymon.ds2.flink.nexmark.sources.GeneratorFunctions;

import org.apache.beam.sdk.nexmark.sources.generator.GeneratorConfig;
import org.apache.beam.sdk.nexmark.sources.generator.model.AuctionGenerator;
import org.apache.beam.sdk.nexmark.sources.generator.model.PersonGenerator;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.core.JsonProcessingException;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.util.Random;

public class PersonGenerationFunction extends GeneratorFunction {


    public PersonGenerationFunction(ObjectMapper objectMapper, Producer<String, byte[]> producer, GeneratorConfig generatorConfig, String kafkaTopic, long epochDurationMs, int ownProportion, int totalProportion) {
        super(objectMapper, producer, generatorConfig, kafkaTopic, epochDurationMs, ownProportion, totalProportion);
    }

    @Override
    public void produceEvent(long eventNumber, Random rnd, long eventTimestampMs) throws JsonProcessingException {
        this.producer.send(new ProducerRecord<String, byte[]>(
                this.kafkaTopic,
                this.objectMapper.writeValueAsBytes(PersonGenerator.nextPerson(
                        eventNumber,
                        rnd,
                        eventTimestampMs,
                        this.generatorConfig)
                )
        ));
    }
}

