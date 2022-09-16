package ch.ethz.systems.strymon.ds2.common;

import org.apache.beam.sdk.nexmark.model.Bid;
import org.apache.beam.sdk.nexmark.model.Person;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;

public class PersonDeserializationSchema implements DeserializationSchema<Person>{


    private static final long serialVersionUID = 1L;
    private static final ObjectMapper objectMapper = new ObjectMapper();


    @Override
    public Person deserialize(byte[] message) throws IOException {
        return objectMapper.readValue(message, Person.class);
    }

    @Override
    public boolean isEndOfStream(Person nextPerson) {
        return false;
    }

    @Override
    public TypeInformation<Person> getProducedType() {
        return TypeInformation.of(Person.class);
    }
}
