package ch.ethz.systems.strymon.ds2.flink.nexmark.sources.GeneratorFunctions;
import org.apache.beam.sdk.nexmark.NexmarkConfiguration;
import org.apache.beam.sdk.nexmark.sources.generator.GeneratorConfig;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.core.JsonProcessingException;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;

import org.apache.beam.sdk.nexmark.sources.generator.model.BidGenerator;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.util.Random;

public abstract class GeneratorFunction {
    Producer<String, byte[]> producer;
    ObjectMapper objectMapper;
    GeneratorConfig generatorConfig;

    String kafkaTopic;

    long epochStartTimeMs;
    final long epochDurationMs;
    long eventsPerEpoch;
    long firstEpochEvent;
    long eventsCountSoFar;


    public GeneratorFunction(ObjectMapper objectMapper, GeneratorConfig generatorConfig,
                             Producer<String, byte[]> producer, String kafkaTopic,
                             long epochDurationMs){
        this.objectMapper = objectMapper;
        this.generatorConfig = generatorConfig;

        this.producer = producer;
        this.kafkaTopic = kafkaTopic;

        this.epochDurationMs = epochDurationMs;
        this.epochStartTimeMs = 0;
        this.eventsPerEpoch = 0;
        this.firstEpochEvent = 0;
        this.eventsCountSoFar = 0;
    }

    /**
     * Get the next event ID
     * @return the next event Id
     */
    long getNextEventId(){
        return this.eventsCountSoFar++;
    }


    /***
     * Get the timestamp for the currentEvent. This is calculated by calculating the place of the event in the current
     * epoch. Then, using the interEventDelayUs, the event is given a timestamp in Us.
     * @param epochStartTimeMs The start of the epoch in Ms.
     * @param epochDurationMs The duration of the epoch in Ms.
     * @param eventsPerEpoch The amount of epochs per second.
     * @param firstEventCurrentEpoch The frist eventId of the current epoch.
     * @param eventNumber The eventNumber to determine the timestamp for.
     * @return The timestamp of the current eventNumber in Us.
     */
    public Long getTimestampUsforEvent(long epochStartTimeMs,
                                       long epochDurationMs,
                                       long eventsPerEpoch,
                                       long firstEventCurrentEpoch,
                                       long eventNumber) {
        long epochStartTimeUs = epochStartTimeMs * 1000;
        long epochDurationUs = epochDurationMs * 1000;
        long n = eventNumber - firstEventCurrentEpoch;
        double interEventDelayUs = (double) epochDurationUs / (double) eventsPerEpoch;
        long eventEpochOffsetUs = (long)(interEventDelayUs * n);
        return epochStartTimeUs + eventEpochOffsetUs;
    }

    /**
     * Make generator ready for the next epoch generation.
     * * This adds the epochDurationMS to epochStartTimeMs,
     * * Set the eventsCountSoFar to eventsAfterEpoch (in case we were not able to produce all events)
     * * Set the eventsAfterEpoch to the next amount of epochs we'll generate
     * @param eventsPerEpoch Amount of events this epoch will generate.
     */
    public void setNextEpochSettings(long eventsPerEpoch) {
        if (this.eventsCountSoFar != 0) {
            this.epochStartTimeMs += this.epochDurationMs;
            this.firstEpochEvent = this.firstEpochEvent + this.eventsPerEpoch;
            this.eventsCountSoFar = this.firstEpochEvent;
        }
        this.eventsPerEpoch = eventsPerEpoch;
    }

    public abstract void generateEvent() throws JsonProcessingException;

}
