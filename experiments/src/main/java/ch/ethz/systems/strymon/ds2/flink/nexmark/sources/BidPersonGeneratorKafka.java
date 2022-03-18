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
import org.apache.beam.sdk.nexmark.sources.generator.model.AuctionGenerator;
import org.apache.beam.sdk.nexmark.sources.generator.model.PersonGenerator;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.beam.sdk.nexmark.NexmarkConfiguration;
import org.apache.beam.sdk.nexmark.model.Bid;
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
public class BidPersonGeneratorKafka {

    private volatile boolean running = true;
    private final GeneratorConfig config = new GeneratorConfig(NexmarkConfiguration.DEFAULT, 1, 1000L, 0, 1);
    private long eventsCountSoFarPerson = 0;
    private long eventsCountSoFarAuctions = 0;
    private long eventsCountSoFarBid = 0;
    private int[] query_1_cosine = {249499,242189,238373,254504,241405,240487,233326,231683,218646,203047,196291,189434,185468,161252,157695,154910,130358,122678,111908,115652,103803,81862,89883,79817,70861,55282,55382,46051,61489,52641,45633,47626,54072,63425,60726,72141,68314,75986,91861,84030,105533,105146,124927,138561,144209,145359,156416,166641,188385,191270,207040,205187,225993,218059,223598,229833,245317,236380,256426,248481,258770,248646,257145,245944,234927,238714,230354,232079,216900,213678,207989,187826,179368,165690,153962,143912,145702,127007,119854,117200,94667,100642,76374,78236,64578,68120,49751,46726,55823,53437,40765,45874,49578,45311,55926,55260,76746,80269,76127,92563,90522,111679,125173,125542,130759,142485,159113,176059,188866,187116,205039,208465,213989,217317,224292,244832,248687,240665,255628,257736,247819,247744,241091,248924,236758,226987,235472,225546,220493,204187,203520,182952,178713,178675,160126,153929,142969,129000,127352,119307};
    private int[] query_1_random = {158020,149708,149042,142595,133424,127985,128880,137208,141313,139451,134868,127442,128513,136929,144683,138406,136109,144486,149910,154642,153558,143687,144768,147127,137901,132549,135713,132384,123372,119046,123769,127615,120295,124056,123141,128875,138448,146114,154328,150149,157389,164835,164593,163290,156120,153541,145579,151891,154255,144839,149808,159635,163130,162686,163160,166508,167956,167857,166825,168007,163264,165963,157365,161113,166768,174913,173284,180939,180050,172969,175552,172671,171318,166110,172574,174732,168349,173511,167473,166567,175114,179601,169849,161062,159557,153204,151317,159794,165178,156576,159907,152516,151548,148115,149985,158507,153310,146271,142180,148860,151827,153661,153264,145828,155653,151213,142556,136496,132479,123104,117563,112122,111773,117137,116804,125474,117029,108440,118195,127573,120928,121638,112598,106991,108477,101507,96750,93770,90523,94500,94879,92169,99645,108878,113166,115024,122445,119635,128014,128232};
    private int[] query_1_increasing = {8958,5191,8876,13331,15501,8795,16901,21846,25323,24215,33748,31049,29948,32298,37628,43478,37396,30728,33072,39076,46559,43811,49388,53398,53456,55787,48936,50643,57239,54911,59978,64015,74876,83202,75736,85312,91325,89278,95701,93935,100033,94086,101041,93144,97970,102502,102844,96715,89833,95639,100436,103913,104854,102380,99085,93167,102025,109235,119011,114986,109201,115078,122584,119354,121496,117341,109922,118966,117800,127218,125683,129059,131288,132088,133404,139504,147667,157556,167312,168986,172067,164795,164010,174678,185095,182110,176184,172760,168442,170615,170826,166456,161055,155718,148825,156450,149606,158373,159034,159949,169795,180566,186387,178612,177081,171402,167717,165486,164607,172621,166626,163288,163807,155808,160461,153954,164608,175350,181154,174654,167240,163806,160575,153032,156627,165418,175693,181270,173544,181817,176497,183455,186142,187517,180646,178100,176912,178977,174744,171427};
    private int[] query_1_decreasing = {235731,228884,236569,228776,231371,236551,231568,225753,231439,237599,245611,253863,249193,239868,237163,245400,237214,244933,237687,230031,235255,237925,238220,228895,224188,229170,230140,229671,221491,218180,211591,212276,214779,218407,214092,207891,214769,221369,218042,217601,207429,214474,222466,214191,207032,200605,191480,198458,199243,188844,178584,181793,172111,166025,163298,163311,158637,162420,162058,160483,152084,154681,158982,150975,152777,158779,159728,160630,149750,144031,151130,141925,131273,121021,120359,113735,105777,105344,106751,100034,102024,100370,93123,99057,96625,102324,108697,116842,124078,129424,131116,125515,133752,131131,132889,132570,126177,115106,114688,113097,119646,110879,115359,119649,119719,110077,112188,103345,100917,95294,87676,76872,85422,81447,81984,84482,81106,89418,81061,86791,83905,80866,76022,71602,65816,72007,65433,70119,69221,71170,70868,71569,77944,73768,81609,84146,74404,75270,74159,82103};
    private int[] query_3_cosine = {68821,66993,66474,67951,66620,67681,64027,72838,66036,58813,64137,55708,51039,57104,53513,49657,56102,49740,39008,48351,40500,44924,42906,30668,36308,19559,22498,17469,30524,32864,27982,16571,19680,31868,17599,30191,34169,28944,41070,29918,33777,31066,41466,53699,43745,43586,52709,61129,66967,50271,61325,63079,72612,75695,75977,67292,77078,77578,71028,68657,71735,77545,64504,77098,66793,70542,66124,67304,64103,61827,60352,50402,57361,62046,49207,53588,40191,40594,45762,36137,33989,26679,40970,28374,22107,19005,17259,22159,27716,16409,33803,15984,32436,29701,27842,37233,35639,24040,30614,34153,29485,34186,32403,37876,39365,46345,46165,47945,55846,54740,55333,69120,74044,67318,76495,77646,79493,65280,65939,83011,70604,65093,74961,80346,78419,61671,78925,71749,64653,64948,72432,69178,48806,56074,59687,57979,53908,40636,48239,41801};
    private int[] query_3_random = {42871,39557,38941,39251,39487,39099,36443,40229,38116,29242,21050,13482,14206,17207,25951,28261,31596,28800,37803,30848,37630,32849,30192,26805,30703,24315,32067,25016,29718,38313,30010,35743,34479,26965,29684,22795,29995,27401,18453,19638,15401,22880,25464,17451,24443,22932,18340,15032,16188,11259,5828,13574,8709,10916,16602,11793,14602,5403,3106,6823,755,4786,2427,11129,8281,10004,4824,9878,856,9901,18123,27776,33583,29755,27168,35066,39816,47570,52335,44786,38084,43107,44513,52790,56499,57614,50427,47923,48393,43662,43434,44233,40606,31138,32728,41324,46333,45896,43854,40427,33417,28840,38507,29688,21342,23576,16159,13487,5840,14108,7160,3565,6097,13354,6965,8223,5800,6256,16075,9890,8039,10016,10876,5097,13575,11669,16798,11718,11761,10694,4181,4502,10482,8237,4176,13565,17720,25259,34001,32769};
    private int[] query_3_increasing = {3617,2706,5145,4115,7148,9694,13045,13838,16446,17176,19556,20397,20419,19385,20098,17710,19093,17602,19953,23103,21355,23756,21979,19498,19433,22030,21038,18708,19754,18297,19755,20058,20746,20803,23781,25943,28675,28991,29617,29213,32451,32826,32045,35218,35937,34668,37451,38402,38508,39161,38557,37141,35593,38866,39721,38380,41528,41926,39579,40229,43502,44367,46989,48740,46879,50187,49003,52266,49946,51188,50925,49090,48530,50659,48336,47052,49781,52137,54480,54459,54925,53359,55531,54950,56347,56147,54589,56156,55582,56486,58000,59327,56859,55922,58881,60178,60636,62227,60355,58511,57874,58758,61911,60587,63675,61777,62174,64180,62044,65383,63816,63499,66569,69864,72736,70373,72074,70530,73121,76520,75736,77974,78369,77477,78819,81377,83232,83399,83702,82228,81541,84708,85266,87591,85186,84592,84624,85198,82773,83870};
    private int[] query_3_decreasing = {84020,86785,87139,85154,82662,78982,80489,77663,78081,78574,81279,81120,82849,83410,84960,86570,83824,84121,83603,83292,81903,83655,85404,85182,81942,80916,78915,79896,76525,78056,74649,75237,74370,71558,70843,71202,71131,69021,66859,64210,62310,59985,59838,56876,55446,55762,54090,52456,52674,55120,57887,54575,51591,47893,47753,46095,46297,47664,48620,47800,47048,48218,49969,47970,47031,43540,45318,43105,45504,48173,48866,48261,48127,49992,46766,43032,44306,44053,43614,40175,37041,37618,37910,37865,36630,34330,35163,37775,39171,36560,38575,37224,37260,34172,30416,26736,25530,24154,20708,20931,20965,20073,19106,15445,17655,17646,13864,12401,13404,11491,12115,14712,13627,10406,7043,9232,5941,4021,2152,3897,5489,6472,4699,6381,6981,5345,4815,3260,5153,5058,5021,1581,1776,3701,6653,4153,6732,7826,6671,7984};
    private int[] query_11_cosine = {150776,147573,141451,148119,146074,148114,131444,131642,136379,138960,126292,129139,113554,104837,108663,98321,90428,81761,78813,82992,67417,70498,64472,66956,66174,55825,45630,53279,51634,57678,53500,51434,48717,51764,44976,53845,58573,54515,73059,68209,81149,75197,75797,96324,104396,105149,99080,105097,110903,110963,121215,128840,136965,141647,142564,149889,154538,152954,152429,158893,152446,155701,149568,147638,147084,151690,143447,129390,125376,127924,118648,122022,114650,112667,95716,100340,89866,97396,90378,84494,84809,69543,67038,61875,66491,56438,63853,60496,46435,43313,54066,46136,46635,51763,60140,51628,55048,63211,76024,72024,84740,86073,90951,93618,97757,97093,112779,112111,123404,126750,120946,120712,127776,130299,131924,142474,150522,144487,144149,154449,155129,154139,138962,154923,148770,139155,148183,128807,128844,127159,118821,121243,109033,115367,95741,90462,104035,96493,79653,89346};
    private int[] query_11_random = {98705,107567,106304,98118,97536,103616,107893,100628,109555,101622,95838,89605,88791,85578,94699,90057,96742,97185,105042,106482,115809,115424,108054,109880,100165,95463,94958,89311,87957,93516,84188,89866,87818,81434,82500,76292,77422,82820,85240,87511,86904,87375,88221,90142,88541,86107,80579,87398,84325,91996,88248,89523,82319,86591,77399,74078,71061,64282,59397,64099,73478,71062,78574,87629,91430,93116,85555,79141,73980,74246,74420,67245,67710,63082,53123,55807,57628,60261,68145,58551,53348,55669,45998,53768,49583,45372,49409,45005,50601,48564,53587,45628,38148,42377,41042,36202,40664,44912,51161,49238,52172,53723,53695,53024,45887,39665,32976,23119,26061,21484,30689,40307,35579,42104,51981,57532,58021,56609,57669,58315,56191,47248,45169,52520,45284,37624,45010,35861,30015,39035,38744,46639,56255,61217,71187,66044,61009,56876,54076,47885};
    private int[] query_11_increasing = {4617,11067,7161,3929,852,5307,7095,8807,2718,1697,4964,482,3827,6565,11267,10832,13358,6678,5384,7510,3093,2487,8050,8005,7171,5683,1197,1368,3563,3153,331,164,2922,6819,9571,11576,6987,7596,6096,10417,15005,18103,20846,24271,28101,31136,30865,28294,31228,32563,37794,43449,43897,47641,45074,45435,48875,53472,53280,48310,54988,56409,56187,57838,59913,61813,60749,59971,55404,58082,53126,59230,55855,51799,58244,53674,48901,53875,50305,52989,57563,58584,56339,58944,59616,63575,60530,66948,66230,69369,64687,59780,63292,67199,71016,69341,65585,64577,61261,56759,55604,51803,47243,53361,53155,55468,50726,55260,58540,61329,61519,57488,61150,60503,58266,59797,64127,63234,59408,63567,67091,63230,60049,55691,52404,57081,60355,63593,61209,62742,67623,68538,68011,70878,75311,79449,84540,86556,89316,94599};
    private int[] query_11_decreasing = {150636,145117,142436,138036,134476,136838,137683,142438,143380,144672,148352,141244,136970,131889,136619,132695,126950,123387,127431,122421,121848,117091,115227,116310,117206,121447,119197,119665,124691,126401,126388,130503,127174,124963,129391,131197,132196,136390,130170,128717,126398,125578,121592,126374,123310,118270,116532,114927,114695,107833,110983,111403,111633,109945,109603,113910,117232,116853,117921,119010,111919,114330,115208,119857,118436,123662,126028,125281,125147,125317,126807,129832,134396,134041,136611,136845,135593,138433,139299,139735,140944,141136,140242,140625,138745,136350,130270,130940,124887,124947,120354,123616,117904,113186,112147,116603,111910,111333,105432,109570,110300,113834,116536,111634,105788,108360,101260,104864,108048,106491,103445,107020,108440,103529,98886,100345,103366,101608,102554,105087,98405,102682,97075,96949,91370,84288,77462,76675,73175,70904,72586,76861,74154,74466,68635,68453,69554,70251,71577,67687};

    private final int rate;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public BidPersonGeneratorKafka(int srcRate) {
        this.rate = srcRate;
    }

    public int getPerSecondRate(long time, int cosine_period, int amplitude, int vertical_shift, int horizontal_shift, int zero_time) {
        int elapsed_minutes = (int)Math.floor((double) ((System.currentTimeMillis() - time) / 60000));
        double period = 2 * Math.PI / cosine_period;
        int limit;
        if ((System.currentTimeMillis() - time) / 60000 < 10){
            limit = (int) (vertical_shift + amplitude * Math.cos(period * (horizontal_shift + 10)));
        }
        else if ((System.currentTimeMillis() - time) / 60000 > zero_time){
            limit = 1000;
        }
        else {
            limit = (int) (vertical_shift + amplitude * Math.cos(period * (horizontal_shift + elapsed_minutes)));
        }

        return limit;

    }

    public int getExperimentRate(long time, String query, String load_pattern){
        int elapsed_minutes = (int)Math.floor((double) ((System.currentTimeMillis() - time) / 60000));
        int limit = 1000;
        if (query.equals("query-1") && load_pattern.equals("cosine") && elapsed_minutes < 140){
            limit = query_1_cosine[elapsed_minutes];
        } else if (query.equals("query-1") && load_pattern.equals("random") && elapsed_minutes < 140){
            limit = query_1_random[elapsed_minutes];
        } else if (query.equals("query-1") && load_pattern.equals("increasing") && elapsed_minutes < 140){
            limit = query_1_increasing[elapsed_minutes];
        } else if (query.equals("query-1") && load_pattern.equals("decreasing") && elapsed_minutes < 140){
            limit = query_1_decreasing[elapsed_minutes];
        } else if (query.equals("query-3") && load_pattern.equals("cosine") && elapsed_minutes < 140){
            limit = query_3_cosine[elapsed_minutes];
        } else if (query.equals("query-3") && load_pattern.equals("random") && elapsed_minutes < 140){
            limit = query_3_random[elapsed_minutes];
        } else if (query.equals("query-3") && load_pattern.equals("increasing") && elapsed_minutes < 140){
            limit = query_3_increasing[elapsed_minutes];
        } else if (query.equals("query-3") && load_pattern.equals("decreasing") && elapsed_minutes < 140){
            limit = query_3_decreasing[elapsed_minutes];
        } else if (query.equals("query-11") && load_pattern.equals("cosine") && elapsed_minutes < 140){
            limit = query_11_cosine[elapsed_minutes];
        } else if (query.equals("query-11") && load_pattern.equals("random") && elapsed_minutes < 140){
            limit = query_11_random[elapsed_minutes];
        } else if (query.equals("query-11") && load_pattern.equals("increasing") && elapsed_minutes < 140){
            limit = query_11_increasing[elapsed_minutes];
        } else if (query.equals("query-11") && load_pattern.equals("decreasing") && elapsed_minutes < 140) {
            limit = query_11_decreasing[elapsed_minutes];
        }

        return limit;
    }

    public void run(String[] args) throws Exception {
        final ParameterTool params = ParameterTool.fromArgs(args);
        int experiment_time = params.getInt("time", 160);
        int zero_time = params.getInt("zero-time", 130);
        int cosine_period = params.getInt("period", 90);
        int amplitude = params.getInt("amplitude", 50000);
        int vertical_shift = params.getInt("y-shift", 100000);
        int horizontal_shift = params.getInt("x-shift", 0);
        int mode = params.getInt("mode", 0);
        int rate = params.getInt("rate", 50000);

        int bids_only = params.getInt("bids-only", 0);
        final String bids_topic = params.get("bids_topic", "bids_topic");
        final String person_topic = params.get("person_topic", "person_topic");
        final String auction_topic = params.get("auction_topic", "auction_topic");
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

            //experiment modes
            int current_rate;
            if (mode == 0){
                current_rate = getExperimentRate(start_time, "query-1", "cosine");
            }
            else if (mode == 1){
                current_rate = getExperimentRate(start_time, "query-1", "random");
            }
            else if (mode == 2){
                current_rate = getExperimentRate(start_time, "query-1", "increasing");
            }
            else if (mode == 3){
                current_rate = getExperimentRate(start_time, "query-1", "decreasing");
            }
            else if (mode == 4){
                current_rate = getExperimentRate(start_time, "query-3", "cosine");
            }
            else if (mode == 5){
                current_rate = getExperimentRate(start_time, "query-3", "random");
            }
            else if (mode == 6){
                current_rate = getExperimentRate(start_time, "query-3", "increasing");
            }
            else if (mode == 7){
                current_rate = getExperimentRate(start_time, "query-3", "decreasing");
            }
            else if (mode == 8){
                current_rate = getExperimentRate(start_time, "query-11", "cosine");
            }
            else if (mode == 9){
                current_rate = getExperimentRate(start_time, "query-11", "random");
            }
            else if (mode == 10){
                current_rate = getExperimentRate(start_time, "query-11", "increasing");
            }
            else if (mode == 11){
                current_rate = getExperimentRate(start_time, "query-11", "decreasing");
            }
            else if (mode == 12){
                current_rate = getPerSecondRate(start_time, cosine_period, amplitude, vertical_shift, horizontal_shift, zero_time);
            } else {
                current_rate = rate;
            }

            if (bids_only == 0){
                for (int i = 0; i < current_rate; i++) {

                    long nextId = nextIdBid();
                    Random rnd = new Random(nextId);

                    // When, in event time, we should generate the event. Monotonic.
                    long eventTimestamp =
                            config.timestampAndInterEventDelayUsForEvent(
                                    config.nextEventNumber(eventsCountSoFarBid)).getKey();
                    producer.send(new ProducerRecord<String, byte[]>(bids_topic, objectMapper.writeValueAsBytes(BidGenerator.nextBid(nextId, rnd, eventTimestamp, config))));
                    eventsCountSoFarBid++;
                }
                }
            else{
                for (int i = 0; i < current_rate; i++) {
                    if (i % 2 == 0) {
                        long eventTimestamp =
                                config.timestampAndInterEventDelayUsForEvent(
                                        config.nextEventNumber(eventsCountSoFarPerson)).getKey();
                        long nextId = nextIdPerson();
                        Random rnd = new Random(nextId);
                        producer.send(new ProducerRecord<String, byte[]>(person_topic, objectMapper.writeValueAsBytes(PersonGenerator.nextPerson(nextId, rnd, eventTimestamp, config))));
                        eventsCountSoFarPerson++;

                    } else {
                        long eventTimestamp =
                                config.timestampAndInterEventDelayUsForEvent(
                                        config.nextEventNumber(eventsCountSoFarAuctions)).getKey();
                        long nextId = nextIdAuctions();
                        Random rnd = new Random(nextId);
                        producer.send(new ProducerRecord<String, byte[]>(auction_topic, objectMapper.writeValueAsBytes(AuctionGenerator.nextAuction(eventsCountSoFarAuctions, nextId, rnd, eventTimestamp, config))));
                        eventsCountSoFarAuctions++;
                    }
                }
            }

            // Sleep for the rest of timeslice if needed
            long emitTime = System.currentTimeMillis() - emitStartTime;
            if (emitTime < 1000) {
                Thread.sleep(1000 - emitTime);
            }
        }
    }

    private long nextIdBid() {
        return config.firstEventId + config.nextAdjustedEventNumber(eventsCountSoFarBid);
    }


    private long nextIdPerson() {
        return config.firstEventId + config.nextAdjustedEventNumber(eventsCountSoFarPerson);
    }

    private long nextIdAuctions() {
        return config.firstEventId + config.nextAdjustedEventNumber(eventsCountSoFarAuctions);
    }


    public static void main(String[] args){
        BidPersonGeneratorKafka test = new BidPersonGeneratorKafka(10000);
        try{
            test.run(args);
            Thread.sleep(1200000);
        }
        catch (Exception e){
            System.out.println(e);
        }
    }

}