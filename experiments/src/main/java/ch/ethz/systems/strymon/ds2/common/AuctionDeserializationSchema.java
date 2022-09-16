package ch.ethz.systems.strymon.ds2.common;

import org.apache.beam.sdk.nexmark.model.Bid;
import org.apache.beam.sdk.nexmark.model.Auction;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;

public class AuctionDeserializationSchema implements DeserializationSchema<Auction>{


        private static final long serialVersionUID = 1L;
        private static final ObjectMapper objectMapper = new ObjectMapper();


        @Override
        public Auction deserialize(byte[] message) throws IOException {
        return objectMapper.readValue(message, Auction.class);
    }

        @Override
        public boolean isEndOfStream(Auction nextAuction) {
        return false;
    }

        @Override
        public TypeInformation<Auction> getProducedType() {
        return TypeInformation.of(Auction.class);
    }
    }
