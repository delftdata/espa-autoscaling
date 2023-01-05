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

package ch.ethz.systems.strymon.ds2.flink.nexmark.sources;

import ch.ethz.systems.strymon.ds2.flink.nexmark.sources.LoadPattern.*;
import org.apache.commons.lang3.NotImplementedException;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import java.text.ParseException;
import java.util.*;


/*
 * Required parameters
 *   Load pattern selection
 *     Required parameters:
 *          load-pattern: STRING {"cosine", "random", "decrease", "increase"}
 *              Load pattern to use during experiment. Possible configurations:  {"cosine", "random", "decrease",
 *              "increase", "testrun", "testrun-scaleup", "testrun-scaledown"}
 *
 *     Optional parameters
 *          query (1) : INT {1, 3, 11}
 *              Query to perform the experiments on (default = 1). Possible configurations: {1, 3, 11}
 *          use-default-configuration (true): BOOLEAN
 *              Use default configurations of load patterns (default = true)
 *          experiment-length (140): INT
 *              Total length of the experiment (default = 140 minutes)
 *          use-seed (1066): INT
 *              Seed to use for load pattern generation (default = 1066)
 *     Configuration specific parameters
 *          load-pattern = "cosine" && use-default-configuration = false
 *              cosine-period: INT
 *                  Time in minutes in which the input rate performs one cosine pattern
 *              input-rate-mean: INT
 *                  Mean input-rate
 *              input-rate-maximum-divergence: INT
 *                  Amount of events the pattern diverges from the mean value
 *              max-noise: INT
 *                  Amount of noise introduced
 *              Additional optional parameters
 *                  upspike-chance: DOUBLE
 *                          Chance to have an upsike-chance event. Default is defined by CosineLoadPattern.
 *                              (Default = 0.0)
 *                  upspike-maximum-period: INT
 *                          Maximum period in which an upspike event can happen. Default is defined by CosineLoadpattern.
 *                              (Default = 3)
 *                  upspike-maximum-input-rate: INT
 *                          Maximum increase in input rate during upspike event. Default is deifned by CosineLoadPattern.
 *                              (Default = 2 * input-rate-maximum-divergence
 *                  upspike-minimum-input-rate: INT
 *                          Minimum increase in input rate during upspike event. Default is defined by CosineLoad Pattern.
 *                              (Default = upspike-maximum-input-rate / 2)
 *                  downspike-chance: DOUBLE
 *                          Chance to have an downspike-chance event. Default is defined by CosineLoadPattern.
 *                              (Default = 0.0)
 *                  downspike-maximum-period: INT
 *                          Maximum period that a downspike event takes. Default is defined by CosineLoadpattern.
 *                              (Default = 3)
 *                  downspike-minimum-input-rate: INT
 *                          Minimum decrease  in input rate during a downspike event. Default is defined by CosineLoad Pattern.
 *                              (Default = 2 * input-rate-maximum-divergence)
 *                  downspike-maximum-input-rate: INT
 *                          Maximum decrease in input rate during a downspike event. Default is defined by CosineLoadPattern.
 *                              (Default = downspike-minimum-input-rate / 2

 *
 *          load-pattern = "random" && & use-default-configuration = false
 *              initial-input-rate: INT
 *                  Input rate to start with
 *              min-divergence: INT
 *                  Minimum increase (decrease if negative) per minute
 *              max-divergence: INT
 *                  Maximum increase (decrease if negative) per minute
 *          load-pattern = "testrun" && use-default-configuration = false
 *              inputrate0: INT
 *              inputrate1: INT
 *              inputrate2: INT
 *
 *   Kafka setup
 *     Required paramters:
 *          enable-bids-topic (false): BOOLEAN
 *                Generate bids topic events. Default value: false
 *          enable-person-topic (false): BOOLEAN
 *                Generate person topic events. Default value: false
 *          enable-auction-topic (false): BOOLEAN
 *                Generate auction topic events. Default value: false
 *      Optional parameters
 *          kafka-server: STRING ("kafka-service:9092")
 *                Kafka server location. Default value: "kafka-service:9092"
 *
 *   Generator setup
 *          iteration-duration-ms (60000): Int
 *                Duration of an iteration in ms. An iteration is the period in which a specific input rate from the
 *                load pattern is being generated. Default value: 60_000ms.
 *          epoch-duration-ms (1000): Int
 *                Duration of an epoch in ms. iteration_duration_ms should be dividable by epoch-duration-ms for the
 *                best generator-performance.
 *          generatorParallelism (1): Int
 *                Amount of threads that running simultaneously while generating data. Default value: 1.
 *
 *    Other
 *      Optional parameters
 *          debugging: BOOLEAN (false)
 *                Enable debugging mode. Default value: false
 */




/**
 * A ParallelSourceFunction that generates Nexmark Bid data
 */
@SuppressWarnings("ALL")
public class BidPersonGeneratorKafka {


    private volatile boolean running = true;

    private List<Integer> loadPattern;

    private boolean debuggingEnabled = false;

    public void log(String message) {
        if (this.debuggingEnabled) {
            System.out.println(message);
        }
    }

    public LoadPattern getCosineLoadPattern(int query, int experimentLength, boolean useDefaultConfigurations,
                                            ParameterTool params) {
        /**
         * Custom paramters:
         *   cosine-period: INT
         *      Time in minutes in which the input rate performs one cosine pattern
         *   input-rate-mean: INT
         *      Mean input-rate
         *   input-rate-maximum-divergence: INT
         *      Amount of events the pattern diverges from the mean value
         *   max-noise: INT
         *      Amount of noise introduced
         */
        CosineLoadPattern loadPattern;
        if (useDefaultConfigurations) {
            loadPattern =  new CosineLoadPattern(query, experimentLength);
            int maxNoise = params.getInt("max-noise", -1);
            if (maxNoise != -1){
                loadPattern.setMaxNoise(maxNoise);
            }
        } else {
            int cosinePeriod = params.getInt("cosine-period");
            int inputRateMaximumDivergence = params.getInt("input-rate-maximum-divergence");
            int inputRateMean = params.getInt("input-rate-mean");
            int maxNoise = params.getInt("max-noise");
            loadPattern = new CosineLoadPattern(query, experimentLength, cosinePeriod, inputRateMaximumDivergence, inputRateMean, maxNoise);
        }

        // optional spike paramters
        double spikeUpChance = params.getDouble("upspike-chance", -1d);
        if (spikeUpChance != -1){
            loadPattern.setSpikeUpChance(spikeUpChance);
        }
        int spikeUpMaximumPeriod = params.getInt("upspike-maximum-period", -1);
        if (spikeUpMaximumPeriod != -1) {
            loadPattern.setSpikeUpMaximumPeriod(spikeUpMaximumPeriod);
        }
        int spikeUpMaximumInputRate = params.getInt("upspike-maximum-input-rate", -1);
        int spikeUpMinimumInputRate = params.getInt("upspike-minimum-input-rate", -1);
        if (spikeUpMaximumInputRate != -1) {
            if (spikeUpMinimumInputRate != -1) {
                loadPattern.setSpikeUpInputRateRange(spikeUpMinimumInputRate, spikeUpMaximumInputRate);
            } else {
                loadPattern.setSpikeUpInputRateRange(spikeUpMaximumInputRate);
            }
        }

        double spikeDownChance = params.getDouble("downspike-chance", -1d);
        if (spikeDownChance != -1){
            loadPattern.setSpikeDownChance(spikeDownChance);
        }
        int spikeDownMaximumPeriod = params.getInt("downspike-maximum-period", -1);
        if (spikeDownMaximumPeriod != -1) {
            loadPattern.setSpikeDownMaximumPeriod(spikeDownMaximumPeriod);
        }
        int spikeDownMaximumInputRate = params.getInt("downspike-maximum-input-rate", -1);
        int spikeDownMinimumInputRate = params.getInt("downspike-minimum-input-rate", -1);
        if (spikeDownMaximumInputRate != -1) {
            if (spikeDownMinimumInputRate != -1) {
                loadPattern.setSpikeDownInputRateRange(spikeDownMinimumInputRate, spikeDownMaximumInputRate);
            } else {
                loadPattern.setSpikeDownInputRateRange(spikeDownMaximumInputRate);
            }
        }

        return loadPattern;
    }
    public LoadPattern getRandomLoadPattern(int query, int experimentLength, boolean useDefaultConfigurations,
                                            ParameterTool params) {
        /**
         * Custom paramters:
         *   initial-input-rate: INT
         *      Input rate to start with
         *   min-divergence: INT
         *      Minimum increase (decrease if negative) per minute
         *   max-divergence: INT
         *      Maximum increase (decrease if negative) per minute
         */
        if (useDefaultConfigurations) {
            return new RandomLoadPattern(query, experimentLength);
        } else {
            int initialInputRate = params.getInt("initial-input-rate");
            int minDivergence = params.getInt("min-divergence");
            int maxDivergence = params.getInt("max-divergence");
            int maxInputRate = params.getInt("max-input-rate", Integer.MAX_VALUE);
            return new RandomLoadPattern(query, experimentLength, initialInputRate, minDivergence, maxDivergence, maxInputRate);
        }
    }

    public LoadPattern getIncreaseLoadPattern(int query, int experimentLength, boolean useDefaultConfigurations) {
        /**
         * Custom paramters:
         * - Not implemented
         */
        if (useDefaultConfigurations) {
            return new IncreaseLoadPattern(query, experimentLength);
        } else {
            throw new NotImplementedException("Custom configuration of the increase loadpattern is not implemented.");
        }
    }

    public LoadPattern getDecreaseLoadPattern(int query, int experimentLength, boolean useDefaultConfigurations)  {
        /**
         * Custom paramters:
         * - Not implemented
         */
        if (useDefaultConfigurations) {
            return new DecreaseLoadPattern(query, experimentLength);
        } else {
            throw new NotImplementedException("Custom configuration of the decrease loadpattern is not implemented.");
        }
    }

    public LoadPattern getTestRun_ScaleUp() {
        return new TestrunLoadPattern(true);
    }

    public LoadPattern getTestRun_ScaleDown() {
        return new TestrunLoadPattern(false);
    }

    public LoadPattern getTestRun(int query, int experimentLength, boolean useDefaultConfigurations,
                                  ParameterTool params)  {
        /**
         * Custom paramters:
         * - inputrate0: int
         * - inputrate1: int
         * - inputrate2: int
         */
        if (useDefaultConfigurations) {
            // TestRun has already a default experimentLength defined in its class.
            // Changing its expeirmentLength can only be done via non-default configuration
            return new TestrunLoadPattern(query, experimentLength);
        } else {
            int inputrate0 = params.getInt("inputrate0");
            int inputrate1 = params.getInt("inputrate1");
            int inputrate2 = params.getInt("inputrate2");
            return new TestrunLoadPattern(query, experimentLength, inputrate0, inputrate1, inputrate2);
        }
    }

    /**
     * Get a loadpattern based on paramters provided by params
     * @param params parameters passed through args.
     * @return LoadPattern class based on parameters
     * @throws Exception Throw exception when invalid parameters are provided.
     */
    public LoadPattern getLoadPattern(ParameterTool params) throws Exception{

        // REQUIRED
        String loadPatternName = params.getRequired("load-pattern");
        this.log("Set loadpatternName to " + loadPatternName);
        int query = params.getInt("query", 1);
        this.log("Set query to " + query);


        // OPTIONAL
        boolean useDefaultConfiguration = params.getBoolean("use-default-configuration", true);
        int experimentLength = params.getInt("experiment-length", 140);
        int seed = params.getInt("use-seed", 1066);
        LoadPattern loadPattern = null;
        switch (loadPatternName) {
            case "cosine": {
                loadPattern = this.getCosineLoadPattern(query, experimentLength, useDefaultConfiguration, params);
                break;
            }
            case "random": {
                loadPattern = this.getRandomLoadPattern(query, experimentLength, useDefaultConfiguration, params);
                break;
            }
            case "increase": {
                loadPattern = this.getIncreaseLoadPattern(query, experimentLength, useDefaultConfiguration);
                break;
            }
            case "decrease": {
                loadPattern = this.getDecreaseLoadPattern(query, experimentLength, useDefaultConfiguration);
                break;
            }
            case "testrun-scaleup": {
                loadPattern = this.getTestRun_ScaleUp();
                break;
            }
            case "testrun-scaledown": {
                loadPattern = this.getTestRun_ScaleDown();
                break;
            }
            case "testrun": {
                loadPattern = this.getTestRun(query, experimentLength, useDefaultConfiguration, params);
                break;
            }
            default: {
                throw new ParseException("Loadpattern " + loadPatternName + " is not recognized.", 0);
            }
        }
        loadPattern.setSeed(seed);
        return loadPattern;
    }

    public void run(String[] args) throws Exception {
        final ParameterTool params = ParameterTool.fromArgs(args);
        this.debuggingEnabled = params.getBoolean("debugging", false);
        this.log("Set debuggingEnabled to " + this.debuggingEnabled + ".");

        /**
         * Load pattern generation
         */
        LoadPattern loadPatternConfiguration = this.getLoadPattern(params);
        List<Integer> loadPattern = loadPatternConfiguration.getLoadPattern().f1;
        System.out.println("Running workbench with the following loadpattern:\n\"\"\"\n" +
                loadPatternConfiguration.getLoadPatternTitle() + "\n\"\"\"");
        if (this.debuggingEnabled) { loadPatternConfiguration.plotLoadPattern(); }

        String kafkaServer = params.get("kafka-server", "kafka-service:9092");

        boolean bidsTopicEnabled = params.getBoolean("enable-bids-topic", false);
        boolean personTopicEnabled = params.getBoolean("enable-person-topic", false);
        boolean auctionTopicEnabled = params.getBoolean("enable-auction-topic", false);

        if (!bidsTopicEnabled && !personTopicEnabled && !auctionTopicEnabled) {
            bidsTopicEnabled = true;
            System.out.println("Warning: No topics are enabled. Bids topic is enabled by default.");
        }
        System.out.println("The following topics are enabled:" + (bidsTopicEnabled ? " bids-topic": "")
                + (personTopicEnabled ? " person-topic": "")  + (auctionTopicEnabled ? " auction-topic": "")
        );

        int epochDurationMs = params.getInt("epoch-duration-ms", 100);
        int iterationDurationMs = params.getInt("iteration-duration-ms", 60_000);
        if (iterationDurationMs % epochDurationMs != 0) {
            System.out.println("Warning: for most accurate performance, iterationDurationMs (" + iterationDurationMs +
                    "ms) should be dividable by epoch-duration-ms (" + epochDurationMs + "ms)");
        }

        int generatorParallelism = params.getInt("generator-parallelism", 1);

        Set<String> remainingParameters = params.getUnrequestedParameters();
        if (remainingParameters.size() > 0) {
            System.out.println("Warning: did not recognize the following parameters: " + String.join(",", remainingParameters));
        }

        System.out.println("Instantiating generators with parallelism[" + generatorParallelism + "] iterationtime[" +
                iterationDurationMs + "ms] epochduration[" + epochDurationMs + "ms]." );

        /**
         * Beginning event generation
         */
        // Creating producer

        BidPersonAuctionSourceParallelManager sourceManager = new BidPersonAuctionSourceParallelManager(kafkaServer,
                epochDurationMs, personTopicEnabled, auctionTopicEnabled, bidsTopicEnabled, generatorParallelism);

        // Starting iteration
        long start_time = System.currentTimeMillis();
        // While the loadPatternPeriod is not over
        for (int iteration = 0; iteration < loadPatternConfiguration.getLoadPatternPeriod(); iteration++) {
            int iterationInputRatePerSecond = loadPattern.get(iteration);
            System.out.println("Starting iteration " + iteration + " with " + iterationInputRatePerSecond + "r/s after " +
                    (System.currentTimeMillis() - start_time) / 1000 + "s");
            sourceManager.runGeneratorsForPeriod(iterationInputRatePerSecond, iterationDurationMs);
        }
        System.out.println("Finished workbench execution after " +  (System.currentTimeMillis() - start_time) / 1000 +
                " at time "+ System.currentTimeMillis() / 1000 + "s");
    }

    public static void main(String[] args){
        BidPersonGeneratorKafka bidpersonGenerator = new BidPersonGeneratorKafka();
        try{
            bidpersonGenerator.run(args);
            Thread.sleep(1200000);
        }
        catch (Exception e){
            e.printStackTrace();
        }
    }

}