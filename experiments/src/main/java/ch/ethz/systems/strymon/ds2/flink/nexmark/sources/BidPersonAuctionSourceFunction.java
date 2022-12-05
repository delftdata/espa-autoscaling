package ch.ethz.systems.strymon.ds2.flink.nexmark.sources;
import org.apache.beam.sdk.nexmark.NexmarkConfiguration;
import org.apache.beam.sdk.nexmark.sources.generator.GeneratorConfig;
import org.apache.beam.sdk.nexmark.sources.generator.model.AuctionGenerator;
import org.apache.beam.sdk.nexmark.sources.generator.model.PersonGenerator;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.core.JsonProcessingException;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;

import org.apache.beam.sdk.nexmark.sources.generator.model.BidGenerator;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.util.Properties;
import java.util.Random;

public class BidPersonAuctionSourceFunction extends Thread {
    String PERSON_TOPIC = "person_topic";
    String BID_TOPIC = "bids_topic";
    String AUCTION_TOPIC = "auction_topic";

    Producer<String, byte[]> producer;
    ObjectMapper objectMapper;
    GeneratorConfig generatorConfig;

    long epochStartTimeMs;
    final long epochDurationMs;
    public long eventsPerEpoch;
    long firstEpochEvent;
    long eventsCountSoFar;

    boolean enablePersonTopic;
    boolean enableAuctionTopic;
    boolean enableBidTopic;

    int stoppedIterationNumber;

    public BidPersonAuctionSourceFunction(String kafkaServer,
                                          long epochDurationMs,
                                          boolean enablePersonTopic,
                                          boolean enableAuctionTopic,
                                          boolean enableBidTopic){
        // Create producer
        if (kafkaServer != null) {
            // Not in testing environment
            Properties props = new Properties();
            props.put("bootstrap.servers", kafkaServer);
            props.put("acks", "1");
            props.put("retries", "0");
            props.put("linger.ms", "10");
            props.put("compression.type", "lz4");
            props.put("batch.size", "50000");
            props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
            props.put("value.serializer", "org.apache.kafka.common.serialization.ByteArraySerializer");
            this.producer = new KafkaProducer<>(props);
        }


        // Creating object mapper
        this.objectMapper = new ObjectMapper();
        // ConfigGenerator
        this.generatorConfig = new GeneratorConfig(
                NexmarkConfiguration.DEFAULT,
                1,
                1000L,
                0,
                0
        );


        // Topics to generate
        this.enablePersonTopic = enablePersonTopic;
        this.enableAuctionTopic = enableAuctionTopic;
        this.enableBidTopic = enableBidTopic;

        // Set epoch settings
        this.epochDurationMs = epochDurationMs;
        this.epochStartTimeMs = 0;
        this.eventsPerEpoch = 0;
        this.firstEpochEvent = 0;
        this.eventsCountSoFar = 0;

        // Highest iteration number that is stopped
        this.stoppedIterationNumber = 0;
    }

    /**
     * Get the current event number and increment it for next round.
     * @return the next event Id.
     */
    public long getNextEventNumber(){
        return this.eventsCountSoFar++;
    }

    /**
     * Increment the current event number.
     * @param increment How much to increment the current eventsCountSoFar.
     */
    public void incrementEventNumber(long increment) {
        this.eventsCountSoFar += increment;
    }


    /**
     * Get the corresponding timestamp based on eventNumber.
     * @param eventNumber Event number to determine a timestamp for
     * @return Timestamp of event number in Ms.
     */
    public Long getTimestampsMsforEvent(long eventNumber) {
        long timestampUs = this.getTimestampUsforEvent(eventNumber);
        return timestampUs / 1000L;
    }

    /**
     * Get the corresponding timestamp based on eventNumber.
     * @param eventNumber Event number to determine a timestamp for
     * @return Timestamp of event number in Us.
     */
    public Long getTimestampUsforEvent(long eventNumber){
        return this.getTimestampUsforEvent(
                this.epochStartTimeMs,
                this.epochDurationMs,
                this.eventsPerEpoch,
                this.firstEpochEvent,
                eventNumber
        );
    }

    /***
     * Get the timestamp for the currentEvent. This is calculated by calculating the place of the event in the current
     * epoch. Then, using the interEventDelayUs, the event is given a timestamp in Us.
     * If the eventID is from a previous epoch, the first eventIe
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
        if (n < 0) {
            // Something went wrong: n is eventNumber is from a previous epoch. Using smallest timestamp from current
            // epoch.
            n=0;
        }
        double interEventDelayUs = (double) epochDurationUs / (double) eventsPerEpoch;
        long eventEpochOffsetUs = (long)(interEventDelayUs * n);
        return epochStartTimeUs + eventEpochOffsetUs;
    }

    /**
     * Make generator ready for the next epoch generation.
     * * This adds the epochDurationMS to epochStartTimeMs,
     * * Set the eventsCountSoFar to eventsAfterEpoch (in case we were not able to produce all events)
     * * Set the eventsAfterEpoch to the next amount of epochs we'll generate
     * @param totalEpochEvents Amount of events this epoch will generate.
     */
    public void setNextEpochSettings(long totalEpochEvents) {
        if (this.eventsCountSoFar != 0) {
            this.epochStartTimeMs += this.epochDurationMs;
            this.firstEpochEvent = this.firstEpochEvent + this.eventsPerEpoch;
            this.eventsCountSoFar = this.firstEpochEvent;
        }
        this.eventsPerEpoch = totalEpochEvents;
     }

     public int getTotalProportion() {
        int eventsPerEpoch = 0;
        if (this.enablePersonTopic) {
            eventsPerEpoch += GeneratorConfig.PERSON_PROPORTION;
        }
        if (this.enableAuctionTopic) {
            eventsPerEpoch += GeneratorConfig.AUCTION_PROPORTION;
        }
        if (this.enableBidTopic) {
            int bidsProportion = GeneratorConfig.PROPORTION_DENOMINATOR
                    - GeneratorConfig.PERSON_PROPORTION - GeneratorConfig.AUCTION_PROPORTION;
            eventsPerEpoch += bidsProportion;
        }
        return eventsPerEpoch;
     }

    /**
     * Given the total amount of events that have to be genenerated, how much will the ID grow by at the end of
     * the epoch.
     * @param amountOfEvents Amount of events to generate this epoch
     * @return The increase of eventID after generating the provided amount of events
     */
     public int getTotalIdIncrease(long amountOfEvents) {
        double usedProportion = this.getTotalProportion();
        int epochs = (int) Math.ceil((double) amountOfEvents / usedProportion);
        return epochs * GeneratorConfig.PROPORTION_DENOMINATOR;
     }

    /**
     * Generate all events of the epoch.
     * @param totalEpochEvents Amount of events to be generated in this epoch.
     * @throws JsonProcessingException Generator error.
     */
    public void generateAllEpochEvents(long totalEpochEvents, int currentIterationNumber) throws JsonProcessingException {
        this.generatePortionOfEpochEvents(totalEpochEvents, 0, totalEpochEvents , currentIterationNumber);
    }

    /**
     * Generate a portion of all the epoch events.
     * The portion that is generated is on index firstEventIndex - firstEventIndex + eventsToGenerate.
     * @param totalEpochEvents Total events generated in this epoch. Used for ensuring correct ID's.
     * @param firstEventIndex The index of the first event it has to generate.
     * @param eventsToGenerate The amount of events that have to be generated.
     * @throws JsonProcessingException Generator error.
     */
     public void generatePortionOfEpochEvents(long totalEpochEvents, long firstEventIndex, long eventsToGenerate,
                                              int currentIterationNumber) throws JsonProcessingException {
         int totalIdIncrease = this.getTotalIdIncrease(totalEpochEvents);
         this.setNextEpochSettings(totalIdIncrease);

         int beforeIdIncrease = this.getTotalIdIncrease(firstEventIndex);
         this.incrementEventNumber(beforeIdIncrease);

         this.generateEvents(eventsToGenerate, currentIterationNumber);
     }

    /**
     * Generate all events for the upcomming epoch.
     * @param totalEpochEvents Events to produce in this epoch.
     * @param currentIterationNumber The number of the iteration the generator is currently generating events for.
     *                               The generator is only allowed to generate iterations when the currentIterationNumber
     *                               is larger than the stoppedIterationNumber
     * @throws JsonProcessingException Processing error thrown by event generation.
     */
    private void generateEvents(long totalEpochEvents, int currentIterationNumber) throws JsonProcessingException {
        long remainingEpochEvents = totalEpochEvents;
        while (remainingEpochEvents > 0 && currentIterationNumber > this.stoppedIterationNumber){
            long eventNumber = getNextEventNumber();
            long timestampMs = getTimestampsMsforEvent(eventNumber);
            long eventId = eventNumber + this.generatorConfig.firstEventId;
            Random rnd = new Random(eventId);
            long offset = eventId % GeneratorConfig.PROPORTION_DENOMINATOR;
            try {
                if (offset < GeneratorConfig.PERSON_PROPORTION) {
                    if (this.enablePersonTopic) {
                        // produce topic if enabled
                        this.producePersonEvent(eventId, rnd, timestampMs);
                        remainingEpochEvents--;
                    } else {
                        // if not enabled, skip ID's concerning the topic.
                        // Note that we already incremented the eventNumber by 1.
                        this.incrementEventNumber((GeneratorConfig.PERSON_PROPORTION - offset) - 1);
                    }
                } else if (offset < GeneratorConfig.PERSON_PROPORTION + GeneratorConfig.AUCTION_PROPORTION) {
                    if (this.enableAuctionTopic) {
                        // produce topic if enabled
                        this.produceAuctionEvent(eventNumber, eventId, rnd, timestampMs);
                        remainingEpochEvents--;
                    } else {
                        // if not enabled, skip ID's concerning the topic
                        this.incrementEventNumber((GeneratorConfig.AUCTION_PROPORTION -
                                (offset - GeneratorConfig.PERSON_PROPORTION)) - 1);
                    }
                } else {
                    if (this.enableBidTopic) {
                        // produce topic if enabled
                        this.produceBidEvent(eventId, rnd, timestampMs);
                        remainingEpochEvents--;
                    } else {
                        // if not enabled, skip ID's concerning the topic
                        long bidProportion = GeneratorConfig.PROPORTION_DENOMINATOR - GeneratorConfig.PERSON_PROPORTION
                                - GeneratorConfig.AUCTION_PROPORTION;
                        this.incrementEventNumber((bidProportion -
                                (offset - GeneratorConfig.PERSON_PROPORTION - GeneratorConfig.AUCTION_PROPORTION)) - 1);
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

    }


    /**
     * Produce a person event
     * @param eventId Id of the event.
     * @param rnd Random class used for creating the person event.
     * @param eventTimestampMs Timestamp of the event.
     * @throws JsonProcessingException Exception thrown by objectMapper.
     */
    public void producePersonEvent(long eventId, Random rnd, long eventTimestampMs) throws JsonProcessingException {
        this.producer.send(new ProducerRecord<String, byte[]>(
                this.PERSON_TOPIC,
                this.objectMapper.writeValueAsBytes(PersonGenerator.nextPerson(
                        eventId,
                        rnd,
                        eventTimestampMs,
                        this.generatorConfig)
                )
        ));
    }
    /**
     * Produce a person event
     * @param eventId Id of the event.
     * @param eventNumber Number of the event (eventsIDs start at this.generatorConfig.firstEventId)
     * @param rnd Random class used for creating the person event.
     * @param eventTimestampMs Timestamp of the event.
     * @throws JsonProcessingException Exception thrown by objectMapper.
     */
    public void produceAuctionEvent(long eventId, long eventNumber, Random rnd, long eventTimestampMs) throws JsonProcessingException{
        this.producer.send(new ProducerRecord<String, byte[]>(
                this.AUCTION_TOPIC,
                objectMapper.writeValueAsBytes(AuctionGenerator.nextAuction(
                        eventNumber,
                        eventId,
                        rnd,
                        eventTimestampMs,
                        this.generatorConfig)
                )
        ));
    }

    /**
     * Produce a bid event
     * @param eventId Id of the event.
     * @param rnd Random class used for creating the bid event.
     * @param eventTimestampMs Timestamp of the event.
     * @throws JsonProcessingException Exception thrown by objectMapper.
     */
    public void produceBidEvent(long eventId, Random rnd, long eventTimestampMs) throws JsonProcessingException{
        this.producer.send(new ProducerRecord<String, byte[]>(
                this.BID_TOPIC,
                objectMapper.writeValueAsBytes(BidGenerator.nextBid(
                        eventId,
                        rnd,
                        eventTimestampMs,
                        this.generatorConfig)
                )
        ));
    }

}
