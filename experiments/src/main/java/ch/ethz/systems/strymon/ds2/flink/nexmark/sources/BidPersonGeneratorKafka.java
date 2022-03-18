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
    private int[] query_1_cosine = {246795,257528,241363,242938,239897,227725,238390,232215,221448,202336,206039,197705,176974,179406,152347,154285,139417,119912,125287,111911,101769,94332,75870,68231,77000,70502,63554,63299,60196,53642,57825,40812,58711,57101,62243,58027,59895,76676,75467,98514,99073,109537,116302,129025,142895,149170,167333,173691,188078,183320,191471,208168,218817,223711,232259,229290,235394,236498,241576,244062,242098,259205,242739,239499,247852,244059,226393,220115,224879,210350,197319,193863,171540,165528,159709,155010,148202,134140,119786,104824,98247,81559,82438,79853,73309,60150,54196,45572,53817,52276,49587,43627,58243,57080,62240,65050,69755,66999,91640,91137,107654,116686,127277,119523,139334,158325,160778,165356,172788,191094,197838,216648,213611,218300,223764,228762,251330,240852,251931,250608,248768,240927,252142,242280,243602,236977,231951,216001,217240,214507,196677,187859,173111,163869,166150,156171,134920,136062,115730,114658};
    private int[] query_1_random = {157493,160269,161285,157545,151961,161305,156832,164203,169655,174323,169379,163136,159744,163222,160212,155973,154373,146686,147434,152825,157594,164522,157490,161708,164541,161107,156641,165346,161216,170128,164849,157606,165349,160820,161446,170683,166259,157678,155317,160778,166662,161244,156461,149361,154446,164394,172809,181038,178560,173430,179666,174458,173477,180403,188395,197875,195987,203177,201720,199916,192506,195379,190719,198688,197595,205451,214266,205236,209211,218881,210238,215004,222057,216184,212739,216995,225242,221234,213280,203887,194159,188163,195628,190238,193447,193243,201534,198337,191251,195632,203193,196066,202796,198552,198230,190493,185848,189104,179938,180891,171240,166185,159705,152322,142650,141361,143519,142141,142122,143853,137748,146910,142449,146822,156319,149485,153773,157086,159264,158441,160295,153858,147326,148064,147025,144571,145246,143659,149355,154984,156142,146273,140192,132979,136092,126330,121512,119001,123359,129706};
    private int[] query_1_increasing = {11602,16471,21140,15346,10380,7524,19440,26034,23543,30257,32490,42544,44309,44046,37587,29665,28089,30421,38593,43452,53825,56077,53775,50212,44380,49935,46225,40811,43594,48087,40280,42713,49860,50898,54545,49029,51186,54265,57526,50202,45741,48770,54657,54395,55120,53508,47462,53033,49451,48221,40547,39977,41475,37041,30723,27426,20134,24225,33767,28647,32697,31590,29233,35469,31313,26290,20943,31282,34822,42484,40546,37036,34874,43168,46222,52226,47534,45627,42560,44554,51129,46845,40876,33800,41317,35197,28874,37705,37592,39961,32384,34583,32013,41916,47737,53330,47700,50454,46531,39865,47808,43086,37053,44517,50349,61354,63502,72826,80613,88929,94947,105898,105866,115806,123407,128679,125008,123448,134669,126915,134169,136978,134593,134250,142029,143229,152465,163947,158322,157112,153915,151901,144624,142210,150366,160704,166712,166036,177603,183082};
    private int[] query_1_decreasing = {244886,238823,233235,233111,239706,244547,243551,237755,240670,234999,224268,230511,222472,219132,227621,224597,226635,233654,231532,234924,234507,238039,240819,231559,220314,212883,218590,211021,217156,222115,228425,218022,211344,206331,212358,202968,192406,185028,187767,188924,191833,181382,184601,185763,175750,170084,170112,160637,155746,157394,149388,146788,153405,151148,152097,158947,153675,155090,150476,149535,146123,138253,131970,127348,131931,140251,143724,138606,132389,124704,130992,121507,113082,120465,113849,116611,117506,118229,110802,115915,117049,125256,131858,136700,145256,148028,138452,134282,127595,124881,129324,132558,125029,124455,122392,110994,106285,102714,107723,110060,102737,94146,83939,85797,75269,80700,78232,76855,72984,66431,56430,45335,48528,56821,61012,51008,50920,42750,31659,25970,23635,31575,36211,30624,23609,28243,29072,36100,44141,33877,25861,29333,29771,28644,30248,26123,33269,35576,34445,26855};
    private int[] query_3_cosine = {72260,74588,79939,68223,75798,71502,64850,60704,64215,56876,58680,54846,66832,58923,46632,50219,41009,53810,35436,38625,41826,41051,41369,26054,27817,28951,30804,22860,29768,20830,21106,32898,35257,24296,25841,28412,29261,36473,31682,41515,31650,38667,37131,52055,43876,56986,50164,51664,67599,60793,52843,55056,75628,78359,76769,65506,77895,78775,70159,77090,80512,84489,68361,73768,80626,66178,76759,72574,69990,68267,68475,69045,59786,55835,54632,55132,47488,46204,49404,30255,42714,31018,42111,30624,34390,19235,28431,33698,32346,19416,28675,32914,27554,21513,21884,28787,22730,38057,42057,39456,34681,34414,42191,54130,46454,56653,55952,45437,50566,57524,70792,68676,73046,66969,63611,68615,75211,79459,73635,79422,76623,72070,81418,67262,82146,81221,70847,76942,59520,59931,67118,54103,61811,60844,60374,41056,54168,39183,47653,46083};
    private int[] query_3_random = {53885,62584,65163,62550,60441,57878,66177,71423,71264,81180,84503,83166,91975,101053,107876,101849,105122,107885,109083,100116,96892,89510,79789,78280,71199,66605,73489,70963,77727,71056,62343,68184,65617,73698,72833,80839,71586,70527,60670,64612,66436,75097,71253,77976,68328,69438,76088,76437,67911,58896,60191,63820,68787,74936,65584,75184,80232,84447,91563,89807,92353,87311,78318,85528,89926,97773,100052,102910,109467,112863,107143,109082,117022,118117,124887,134252,128523,136866,146686,137072,139208,147530,144601,136513,135063,142311,142128,139450,132984,142891,142081,137251,127711,128442,120081,127307,136294,128559,122920,121165,123637,114347,106901,110425,112416,121457,130795,128998,122143,128796,126004,124251,133891,141171,146392,153265,145662,152103,155966,157875,166107,174655,170161,170722,173505,165188,171530,162764,170183,174263,181764,181459,175122,165463,167155,175605,168842,170598,170763,169287};
    private int[] query_3_increasing = {5574,8951,6873,6766,9687,9045,11141,14416,14708,16721,16659,17594,15815,16601,19397,19156,21976,22314,20640,20224,18373,20433,22227,23777,22163,25441,23592,21155,21465,22803,25783,23590,21613,23230,24387,28132,25655,27669,27774,30544,34139,33223,33433,35624,33653,37299,35825,37212,36013,37212,37526,38928,39515,43129,43338,42251,43307,41004,43166,42061,44528,47906,46307,45717,43819,44275,44904,48071,46009,44268,44284,45500,48164,49270,48629,47047,46682,47898,48385,48018,48829,46721,45701,45598,43872,47237,46376,48427,50665,54309,53893,55609,59119,62110,62168,65294,63989,66445,65531,68524,68909,68205,70340,69830,70284,68209,69122,72465,74287,72619,70424,73413,71852,70609,72172,73882,75294,74863,76979,77132,78656,80275,79858,79263,80995,80666,80117,78464,76561,79492,78747,80582,79612,81585,81715,82049,82342,83302,80836,81517};
    private int[] query_3_decreasing = {79251,80270,81434,77900,78159,77332,75174,75013,73426,72839,70151,67486,68352,68475,70983,72842,72805,70506,71852,72825,74704,72357,74255,73048,71770,73245,70308,67399,64483,65142,67957,69942,68540,69846,69945,70734,67834,66897,68717,65755,66165,62498,60223,62430,61359,63384,62441,61044,62281,60823,61702,63133,64417,62300,60128,57637,57395,56107,53200,50587,52903,53832,53443,56088,58337,56000,56381,57309,54910,55263,54638,54551,53968,51224,51336,48707,45021,43785,40214,40903,38216,34818,36206,35462,33317,31968,34518,33999,36267,38886,38724,36272,34591,33264,33630,30458,31960,32800,35220,33800,35414,32497,28696,27349,24839,21844,20508,21175,22083,22481,25002,22130,24673,27307,27567,26949,25682,23034,21446,18235,18564,17262,15752,16143,13829,13680,11285,7546,6451,3444,5078,3200,4701,2487,5069,5301,2580,1739,854,843};
    private int[] query_11_cosine = {141648,155395,156145,157486,144048,152944,134486,134575,136059,124756,118914,112031,122999,105728,103186,106345,88924,81196,77395,84781,71410,75459,74307,58939,61966,50363,50404,47163,52608,51184,46694,41010,43383,59973,50074,58312,61714,66240,64971,65888,69980,70671,81792,87085,99295,95088,104334,103287,116928,112111,132867,136311,141571,127550,141076,149789,151839,139754,156486,152032,144249,142736,147462,146251,146948,148559,134216,137228,128839,123060,124539,120374,119873,105383,96240,98972,88291,84952,91738,71851,79036,75734,70307,58719,50631,66581,44336,49316,48174,48842,53265,49505,58334,54787,52933,64957,51089,58608,57288,79671,66412,87549,84535,98534,100633,92754,100054,118661,109697,112525,131741,130322,135529,135594,141324,151784,144800,150408,151668,143459,149414,146684,152917,147109,146707,152617,138234,139371,140663,135021,120117,123162,107152,106221,97540,94302,89359,81928,93552,86774};
    private int[] query_11_random = {90302,81344,71585,75115,76672,68903,70406,64984,61713,61884,61322,56376,49348,50241,43598,43521,39451,37684,34270,29839,20907,25295,27879,33297,30151,33356,42001,47575,46974,37304,39240,33952,33776,28821,20186,29527,27517,28274,20631,11981,8439,15798,17289,17904,23913,19821,17920,16917,14150,18108,16497,16316,12610,11527,18282,17485,21772,20035,21221,19415,14631,21871,13475,18677,19825,15990,15034,18023,26213,22848,31675,29916,21561,25383,27169,35633,39465,37844,45064,53193,49352,53313,50492,52930,59688,60146,66040,57230,64992,62901,66702,60242,66960,59204,65413,57998,53205,49963,40895,48233,48320,46994,47994,56297,49223,39686,36482,46104,43921,35758,41701,34929,35511,36662,43263,45110,43907,48616,43517,44399,38613,35860,39081,31162,23381,33100,41855,46717,48825,50865,48098,43491,41036,44312,51808,42613,40692,42275,38802,42125};
    private int[] query_11_increasing = {2416,3065,3336,3060,2840,3086,3043,2852,2740,3052,3748,4438,4307,4190,4452,5101,5088,5693,5425,5220,5725,5749,6210,5913,5532,5769,5509,5405,6054,6631,6708,6304,7021,6927,6823,6743,6801,6392,5956,5784,6032,6287,5904,6486,6114,6588,6992,7615,7648,8139,8190,8814,9532,9231,8769,9127,8958,9305,9476,9859,9500,9886,10532,11221,11612,12200,12632,12942,12510,12586,13289,13928,13904,14501,15242,15266,14969,14679,15418,16009,15881,15424,15143,14835,14628,15247,15899,15887,16191,16448,16142,16130,16162,16485,16176,15911,15524,16056,16262,16250,16744,17488,17816,17345,17175,16848,16660,17042,16977,16791,17314,17660,17494,18202,17990,18383,18033,17942,17444,17390,16932,16945,16736,17481,17159,17289,17600,17501,18126,17921,18412,18924,19201,19686,19552,20148,20500,21193,21017,21024};
    private int[] query_11_decreasing = {16537,16028,15793,15759,15187,15103,14908,15068,14504,15027,14535,14741,14563,14876,14247,13782,13752,13331,13643,13301,13407,13350,13667,13532,13880,14163,14121,13593,13095,13514,13976,14350,14237,14256,13583,13532,13775,13316,13295,13088,13274,13011,13355,13679,13092,12650,12512,12215,12164,12577,12857,12300,12210,12267,11762,12266,11891,11999,12140,11623,11057,10766,10613,10553,10430,10691,10965,10926,11071,10708,10465,10261,10238,10072,9411,9923,9956,10112,9731,9454,8951,8581,8082,8600,8313,8122,8448,8270,8027,7327,6914,6789,6994,7311,7716,7191,7430,7512,7242,7577,8034,7408,7282,6641,6401,5896,5961,5601,5886,5200,5424,5297,5831,6193,6115,6266,6742,6922,6933,6261,6716,6025,6350,6781,6101,5654,5015,4879,5334,4968,5077,5537,5272,4775,4162,3565,3851,4111,3924,3424};


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