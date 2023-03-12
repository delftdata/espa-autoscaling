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

package ch.ethz.systems.strymon.ds2.flink.nexmark.sources.DS2.updated;

import ch.ethz.systems.strymon.ds2.common.BidDeserializationSchema;
import ch.ethz.systems.strymon.ds2.flink.nexmark.sinks.DummyLatencyCountingSink;
import org.apache.beam.sdk.nexmark.model.Bid;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.AssignerWithPeriodicWatermarks;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.kafka.clients.consumer.OffsetResetStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.Nullable;

public class Query5KafkaSource {

    private static final Logger logger  = LoggerFactory.getLogger(Query5KafkaSource.class);

    public static void main(String[] args) throws Exception {

        // Checking input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);

        final String sourceSSG;
        final String sinkSSG;
        final String windowSSG;

        if(params.getBoolean("slot-sharing", false)){
            sourceSSG = "Source";
            sinkSSG = "Sink";
            windowSSG = "WindowedAggregation";
        }
        else{
            sourceSSG = "default";
            sinkSSG = "default";
            windowSSG = "default";
        }

        // set up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        env.getConfig().setAutoWatermarkInterval(1000);

        // enable latency tracking
        // env.getConfig().setLatencyTrackingInterval(5000);

        KafkaSource<Bid> source =
                KafkaSource.<Bid>builder()
                        .setBootstrapServers("kafka-service:9092")
                        .setTopics("bids_topic")
                        .setGroupId("consumer_group")
                        .setProperty("fetch.min.bytes", "1000")
                        .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))
                        .setValueOnlyDeserializer(new BidDeserializationSchema())
                        .build();

        DataStream<Bid> bids = env.fromSource(source, WatermarkStrategy.noWatermarks(), "BidsSource")
                .slotSharingGroup(sourceSSG)
                .setParallelism(params.getInt("p-bids-source", 1))
                .assignTimestampsAndWatermarks(new TimestampAssigner())
                .slotSharingGroup(sourceSSG)
                .uid("BidsSource")
                .name("BidsTimestampAssigner");

        // SELECT B1.auction, count(*) AS num
        // FROM Bid [RANGE 60 MINUTE SLIDE 1 MINUTE] B1
        // GROUP BY B1.auction
        DataStream<Tuple2<Long, Long>> windowed = bids.keyBy(new KeySelector<Bid, Long>() {
                    @Override
                    public Long getKey(Bid bid) throws Exception {
                        return bid.auction;
                    }
                }).timeWindow(Time.minutes(10), Time.minutes(1))
                .aggregate(new CountBids())
                .name("WindowCount")
                .uid("WindowCount")
                .setParallelism(params.getInt("p-window", 1))
                .slotSharingGroup(windowSSG);

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        windowed.transform("DummyLatencySink", objectTypeInfo, new DummyLatencyCountingSink<>(logger))
                .setParallelism(params.getInt("p-sink", 1))
                .slotSharingGroup(sinkSSG)
                .name("LatencySink")
                .uid("LatencySink");

        // execute program
        env.execute("Nexmark Query5 with a Kafka Source");
    }

    private static final class TimestampAssigner implements AssignerWithPeriodicWatermarks<Bid> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Bid element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.dateTime);
            return element.dateTime;
        }
    }

    private static final class CountBids implements AggregateFunction<Bid, Long, Tuple2<Long, Long>> {

        private long auction = 0L;

        @Override
        public Long createAccumulator() {
            return 0L;
        }

        @Override
        public Long add(Bid value, Long accumulator) {
            auction = value.auction;
            return accumulator + 1;
        }

        @Override
        public Tuple2<Long, Long> getResult(Long accumulator) {
            return new Tuple2<>(auction, accumulator);
        }

        @Override
        public Long merge(Long a, Long b) {
            return a + b;
        }
    }
}