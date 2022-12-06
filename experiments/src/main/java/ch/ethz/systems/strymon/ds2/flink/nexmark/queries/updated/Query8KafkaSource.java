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

package ch.ethz.systems.strymon.ds2.flink.nexmark.queries.updated;

import ch.ethz.systems.strymon.ds2.common.AuctionDeserializationSchema;
import ch.ethz.systems.strymon.ds2.common.PersonDeserializationSchema;
import ch.ethz.systems.strymon.ds2.flink.nexmark.sinks.DummyLatencyCountingSink;
import org.apache.beam.sdk.nexmark.model.Auction;
import org.apache.beam.sdk.nexmark.model.Person;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.FlatJoinFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.AssignerWithPeriodicWatermarks;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.util.Collector;
import org.apache.kafka.clients.consumer.OffsetResetStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.Nullable;

public class Query8KafkaSource {

    private static final Logger logger  = LoggerFactory.getLogger(Query8KafkaSource.class);

    public static void main(String[] args) throws Exception {

        // Checking input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);

        final String sourceAuctionSSG;
        final String sourcePersonSSG;
        final String sinkSSG;

        if(params.getBoolean("slot-sharing", false)){
            sourceAuctionSSG = "AuctionSource";
            sourcePersonSSG = "PersonSource";
            sinkSSG = "Sink";
        }
        else{
            sourceAuctionSSG = "default";
            sourcePersonSSG = "default";
            sinkSSG = "default";
        }

        // set up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        env.getConfig().setAutoWatermarkInterval(1000);

        // enable latency tracking
        //env.getConfig().setLatencyTrackingInterval(5000);

        // Flink API doesn't allow to change parallelism or to set a SlotSharingGroup for the join window
        // We set the global parallelism to the desired windowed join parallelism and set individually the parallelism
        // for the other operators. For the SlotSharingGroup, we rely on the default group.
        env.setParallelism(params.getInt("p-window", 1));

        KafkaSource<Person> person_source =
                KafkaSource.<Person>builder()
                        .setBootstrapServers("kafka-service:9092")
                        .setTopics("person_topic")
                        .setGroupId("consumer_group2")
                        .setProperty("fetch.min.bytes", "1000")
                        .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))
                        .setValueOnlyDeserializer(new PersonDeserializationSchema())
                        .build();


        DataStream<Person> persons = env.fromSource(person_source, WatermarkStrategy.noWatermarks(), "personSource")
                .assignTimestampsAndWatermarks(new PersonTimestampAssigner())
                .slotSharingGroup(sourcePersonSSG)
                .setParallelism(params.getInt("p-person-source", 1))
                .uid("PersonSource")
                .name("PersonSource");


        KafkaSource<Auction> auction_source =
            KafkaSource.<Auction>builder()
                .setBootstrapServers("kafka-service:9092")
                .setTopics("auction_topic")
                .setGroupId("consumer_group1")
                .setProperty("fetch.min.bytes", "1000")
                .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))
                .setValueOnlyDeserializer(new AuctionDeserializationSchema())
                .build();

        DataStream<Auction> auctions = env.fromSource(auction_source, WatermarkStrategy.noWatermarks(), "auctionsSource")
                .uid("AuctionSource")
                .name("AuctionSource")
                .assignTimestampsAndWatermarks(new AuctionTimestampAssigner())
                .slotSharingGroup(sourceAuctionSSG)
                .setParallelism(params.getInt("p-auction-source", 1))
                .name("AuctionTimestampAssigner")
                .uid("AuctionTimestampAssigner");

        // SELECT Rstream(P.id, P.name, A.reserve)
        // FROM Person [RANGE 1 HOUR] P, Auction [RANGE 1 HOUR] A
        // WHERE P.id = A.seller;
        DataStream<Tuple3<Long, String, Long>> joined =
                persons.join(auctions)
                .where(new KeySelector<Person, Long>() {
                    @Override
                    public Long getKey(Person p) {
                        return p.id;
                    }
                }).equalTo(
                        new KeySelector<Auction, Long>() {
                            @Override
                            public Long getKey(Auction a) {
                                return a.seller;
                            }
                        })
                .window(TumblingEventTimeWindows.of(Time.seconds(10)))
                .apply(new FlatJoinFunction<Person, Auction, Tuple3<Long, String, Long>>() {
                    @Override
                    public void join(Person p, Auction a, Collector<Tuple3<Long, String, Long>> out) {
                        out.collect(new Tuple3<>(p.id, p.name, a.reserve));
                    }
                });


        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        joined.transform("DummyLatencySink", objectTypeInfo, new DummyLatencyCountingSink<>(logger))
                .slotSharingGroup(sinkSSG)
                .setParallelism(params.getInt("p-sink", 1))
                .uid("LatencySink")
                .name("LatencySink");

        // execute program
        env.execute("Nexmark Query8 with a Kafka Source");
    }

    private static final class PersonTimestampAssigner implements AssignerWithPeriodicWatermarks<Person> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Person element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.dateTime);
            return element.dateTime;
        }
    }

    private static final class AuctionTimestampAssigner implements AssignerWithPeriodicWatermarks<Auction> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Auction element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.dateTime);
            return element.dateTime;
        }
    }

}