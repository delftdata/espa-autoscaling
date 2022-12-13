/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ch.ethz.systems.strymon.ds2.flink.nexmark.sources.DS2;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.beam.sdk.nexmark.NexmarkConfiguration;
import org.apache.beam.sdk.nexmark.sources.generator.GeneratorConfig;
import org.apache.beam.sdk.nexmark.sources.generator.model.BidGenerator;
import org.apache.kafka.clients.producer.KafkaProducer;
import java.util.Properties;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;


import java.util.Random;

/**
 * A ParallelSourceFunction that generates Nexmark Bid data
 */
public class BidSourceFunctionGeneratorKafka {

    private volatile boolean running = true;
    private final GeneratorConfig config = new GeneratorConfig(NexmarkConfiguration.DEFAULT, 1, 1000L, 0, 1);
    private long eventsCountSoFar = 0;
    private final int rate;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public BidSourceFunctionGeneratorKafka(int srcRate) {
        this.rate = srcRate;
    }

    public int getPerSecondRate(long time, int cosine_period, int amplitude, int vertical_shift, int horizontal_shift) {
        int elapsed_minutes = (int)Math.floor((double) ((System.currentTimeMillis() - time) / 60000));
        double period = 2 * Math.PI / cosine_period;
        int limit;
        if ((System.currentTimeMillis() - time) / 60000 < 10){
            limit = (int) (vertical_shift + amplitude * Math.cos(period * (horizontal_shift + 10)));
        }
        else {
            limit = (int) (vertical_shift + amplitude * Math.cos(period * (horizontal_shift + elapsed_minutes)));
        }

        return limit;

    }

    public void run(String[] args) throws Exception {
        final ParameterTool params = ParameterTool.fromArgs(args);
        int experiment_time = params.getInt("time", 120);
        int cosine_period = params.getInt("period", 90);
        int amplitude = params.getInt("amplitude", 50000);
        int vertical_shift = params.getInt("y-shift", 100000);
        int horizontal_shift = params.getInt("x-shift", 0);
        int mode = params.getInt("mode", 1);
        int rate = params.getInt("rate", 50000);

        final String topic = params.get("topic", "topic");
        String kafka_server = params.get("kafka_server","kafka-service:9092");
        Properties props = new Properties();
        props.put("bootstrap.servers", kafka_server);
        props.put("acks", "1");
        props.put("retries", "0");
        props.put("linger.ms", "10");
        props.put("compression.type", "lz4");
        props.put("batch.size", "50000");
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.ByteArraySerializer");
        Producer<String, byte[]> producer = new KafkaProducer<>(props);

        long start_time = System.currentTimeMillis();
        while (((System.currentTimeMillis() - start_time) / 60000) < experiment_time) {
            long emitStartTime = System.currentTimeMillis();

            int current_rate;
            if (mode == 1){
                current_rate = getPerSecondRate(start_time, cosine_period, amplitude, vertical_shift, horizontal_shift);
            } else{
                current_rate = rate;
            }

            for (int i = 0; i < current_rate; i++) {

                long nextId = nextId();
                Random rnd = new Random(nextId);

                // When, in event time, we should generate the event. Monotonic.
                long eventTimestamp =
                        config.timestampAndInterEventDelayUsForEvent(
                                config.nextEventNumber(eventsCountSoFar)).getKey();
                producer.send(new ProducerRecord<String, byte[]>(topic, objectMapper.writeValueAsBytes(BidGenerator.nextBid(nextId, rnd, eventTimestamp, config))));
                eventsCountSoFar++;
            }

            // Sleep for the rest of timeslice if needed
            long emitTime = System.currentTimeMillis() - emitStartTime;
            if (emitTime < 1000) {
                Thread.sleep(1000 - emitTime);
            }
        }
    }

    private long nextId() {
        return config.firstEventId + config.nextAdjustedEventNumber(eventsCountSoFar);
    }

    public static void main(String[] args){
        BidSourceFunctionGeneratorKafka test = new BidSourceFunctionGeneratorKafka(10000);
        try{
            test.run(args);
        }
        catch (Exception e){
            System.out.println(e);
        }
    }

}