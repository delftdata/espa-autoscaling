package ch.ethz.systems.strymon.ds2.common;

import org.apache.beam.sdk.nexmark.model.Bid;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

public class BidDeserializationSchema implements DeserializationSchema<Bid> {

    private static final long serialVersionUID = 1L;
    private static final ObjectMapper objectMapper = new ObjectMapper();


    @Override
    public Bid deserialize(byte[] message) throws IOException {
        return objectMapper.readValue(message, Bid.class);
    }

    @Override
    public boolean isEndOfStream(Bid nextBid) {
        return false;
    }

    @Override
    public TypeInformation<Bid> getProducedType() {
        return TypeInformation.of(Bid.class);
    }
}