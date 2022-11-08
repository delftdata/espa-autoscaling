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

import ch.ethz.systems.strymon.ds2.common.PersonDeserializationSchema;
import ch.ethz.systems.strymon.ds2.common.AuctionDeserializationSchema;

import ch.ethz.systems.strymon.ds2.flink.nexmark.sinks.DummyLatencyCountingSink;
import org.apache.beam.sdk.nexmark.model.Auction;
import org.apache.beam.sdk.nexmark.model.Person;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.state.MapState;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.api.common.typeinfo.TypeHint;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.apache.flink.api.java.typeutils.TupleTypeInfo;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.co.RichCoFlatMapFunction;
import org.apache.flink.util.Collector;
import org.apache.kafka.clients.consumer.OffsetResetStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashSet;

public class Query3KafkaSource {

    private static final Logger logger = LoggerFactory.getLogger(Query3KafkaSource.class);

    public static void main(String[] args) throws Exception {

        // Checking input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);

        final String sourceAuctionSSG;
        final String sourcePersonSSG;
        final String sinkSSG;
        final String filterSSG;
        final String coFlatMapSSG;

        if(params.getBoolean("slot-sharing", false)){
            sourceAuctionSSG = "AuctionSource";
            sourcePersonSSG = "PersonSource";
            sinkSSG = "Sink";
            filterSSG = "Filter";
            coFlatMapSSG = "CoFlatMap";
        }
        else{
            sourceAuctionSSG = "default";
            sourcePersonSSG = "default";
            sinkSSG = "default";
            filterSSG = "default";
            coFlatMapSSG = "default";
        }

        // set up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // enable latency tracking
        // env.getConfig().setLatencyTrackingInterval(5000);

        env.disableOperatorChaining();

        final int max_parallelism_source = params.getInt("source-max-parallelism", 20);

//        DataStream<Auction> auctions = env.addSource(new AuctionSourceFunction(auctionSrcRate))
//                .name("Custom Source: Auctions")
//                .setParallelism(params.getInt("p-auction-source", 1));

        KafkaSource<Auction> auction_source =
                KafkaSource.<Auction>builder()
                        .setBootstrapServers("kafka-service:9092")
                        .setTopics("auction_topic")
                        .setGroupId("consumer_group1")
                        .setProperty("fetch.min.bytes", "1000")
                        .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))
                        .setValueOnlyDeserializer(new AuctionDeserializationSchema())
                        .build();

        DataStream<Auction> auctions =
                env.fromSource(auction_source, WatermarkStrategy.noWatermarks(), "auctionsSource")
                        .setParallelism(params.getInt("p-auction-source", 1))
                        .setMaxParallelism(max_parallelism_source)
                        .uid("auctionsSource")
                        .slotSharingGroup(sourceAuctionSSG);

        KafkaSource<Person> person_source =
                KafkaSource.<Person>builder()
                        .setBootstrapServers("kafka-service:9092")
                        .setTopics("person_topic")
                        .setGroupId("consumer_group2")
                        .setProperty("fetch.min.bytes", "1000")
                        .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))
                        .setValueOnlyDeserializer(new PersonDeserializationSchema())
                        .build();

        DataStream<Person> persons = env.fromSource(person_source, WatermarkStrategy.noWatermarks(), "personSource").setParallelism(params.getInt("p-person-source", 1)).setMaxParallelism(max_parallelism_source)
                .slotSharingGroup(sourcePersonSSG)
                .filter(new FilterFunction<Person>() {
                    @Override
                    public boolean filter(Person person) throws Exception {
                        return (person.state.equals("OR") || person.state.equals("ID") || person.state.equals("CA"));
                    }
                })
                .setParallelism(params.getInt("p-person-source", 1)).slotSharingGroup(filterSSG);

        // SELECT Istream(P.name, P.city, P.state, A.id)
        // FROM Auction A [ROWS UNBOUNDED], Person P [ROWS UNBOUNDED]
        // WHERE A.seller = P.id AND (P.state = `OR' OR P.state = `ID' OR P.state = `CA')

        KeyedStream<Auction, Long> keyedAuctions =
                auctions.keyBy(new KeySelector<Auction, Long>() {
                    @Override
                    public Long getKey(Auction auction) throws Exception {
                        return auction.seller;
                    }
                });

        KeyedStream<Person, Long> keyedPersons =
                persons.keyBy(new KeySelector<Person, Long>() {
                    @Override
                    public Long getKey(Person person) throws Exception {
                        return person.id;
                    }
                });

        DataStream<Tuple4<String, String, String, Long>> joined = keyedAuctions.connect(keyedPersons)
                .flatMap(new JoinPersonsWithAuctions()).name("Incrementaljoin").setParallelism(params.getInt("p-join", 1)).slotSharingGroup(coFlatMapSSG);

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        joined.transform("Sink", objectTypeInfo, new DummyLatencyCountingSink<>(logger))
                .setParallelism(params.getInt("p-join", 1)).slotSharingGroup(sinkSSG);

        // execute program
        env.execute("Nexmark Query3 with a Kafka Source");
    }

    private static final class JoinPersonsWithAuctions extends RichCoFlatMapFunction<Auction, Person, Tuple4<String, String, String, Long>> {

        // person state: id, <name, city, state>
        private MapState<Long, Tuple3<String, String, String>> personMap;;

        // auction state: seller, List<id>
        private MapState<Long, HashSet<Long>> auctionMap;

        @Override
        public void open(Configuration parameters){
            MapStateDescriptor<Long, Tuple3<String, String, String>> personDescriptor =
            new MapStateDescriptor<Long, Tuple3<String, String, String>>(
                    "person-map",
                    BasicTypeInfo.LONG_TYPE_INFO,
                    new TupleTypeInfo<>(BasicTypeInfo.STRING_TYPE_INFO, BasicTypeInfo.STRING_TYPE_INFO, BasicTypeInfo.STRING_TYPE_INFO)
                   );

            personMap = getRuntimeContext().getMapState(personDescriptor);

            MapStateDescriptor<Long, HashSet<Long>> auctionDescriptor =
            new MapStateDescriptor<Long, HashSet<Long>>(
                    "auction-map",
                    BasicTypeInfo.LONG_TYPE_INFO,
                    TypeInformation.of(new TypeHint<HashSet<Long>>(){})
                   );

            auctionMap = getRuntimeContext().getMapState(auctionDescriptor);
        }

        @Override
        public void flatMap1(Auction auction, Collector<Tuple4<String, String, String, Long>> out) throws Exception {
            // check if auction has a match in the person state
            if (personMap.contains(auction.seller)) {
                // emit and don't store
                Tuple3<String, String, String> match = personMap.get(auction.seller);
                out.collect(new Tuple4<>(match.f0, match.f1, match.f2, auction.id));
            } else {
                // we need to store this auction for future matches
                if (auctionMap.contains(auction.seller)) {
                    HashSet<Long> ids = auctionMap.get(auction.seller);
                    ids.add(auction.id);
                    auctionMap.put(auction.seller, ids);
                } else {
                    HashSet<Long> ids = new HashSet<>();
                    ids.add(auction.id);
                    auctionMap.put(auction.seller, ids);
                }
            }
        }

        @Override
        public void flatMap2(Person person, Collector<Tuple4<String, String, String, Long>> out) throws Exception {
            // store person in state
            personMap.put(person.id, new Tuple3<>(person.name, person.city, person.state));

            // check if person has a match in the auction state
            if (auctionMap.contains(person.id)) {
                // output all matches and remove
                HashSet<Long> auctionIds = auctionMap.get(person.id);
                auctionMap.remove(person.id);
                for (Long auctionId : auctionIds) {
                    out.collect(new Tuple4<>(person.name, person.city, person.state, auctionId));
                }
            }
        }
    }

}
