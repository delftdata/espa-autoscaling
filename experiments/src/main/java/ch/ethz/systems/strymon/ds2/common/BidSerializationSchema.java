package ch.ethz.systems.strymon.ds2.common;

import org.apache.beam.sdk.nexmark.model.Bid;
import org.apache.flink.streaming.connectors.kafka.KafkaSerializationSchema;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.core.JsonProcessingException;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.producer.ProducerRecord;
import javax.annotation.Nullable;

import java.io.IOException;

public class BidSerializationSchema implements KafkaSerializationSchema<Bid> {

    private static final ObjectMapper objectMapper = new ObjectMapper();
    private String topic;

    public BidSerializationSchema(){
    }

    public BidSerializationSchema(String topic) {
        this.topic = topic;
    }

    @Override
    public ProducerRecord<byte[], byte[]> serialize(
            final Bid message, @Nullable final Long timestamp) {
        try {
            //if topic is null, default topic will be used
            return new ProducerRecord<>(topic, objectMapper.writeValueAsBytes(message));
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("Could not serialize record: " + message, e);
        }
    }
}