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
public class BidPersonGeneratorKafkaOld {

    private volatile boolean running = true;
    private final GeneratorConfig config = new GeneratorConfig(NexmarkConfiguration.DEFAULT, 1, 1000L, 0, 1);
    private long eventsCountSoFarPerson = 0;
    private long eventsCountSoFarAuctions = 0;
    private long eventsCountSoFarBid = 0;

    private int[] query_1_cosine_60_min = {249499,242189,238373,254504,241405,240487,233326,231683,218646,203047,196291,189434,185468,161252,157695,154910,130358,122678,111908,115652,103803,81862,89883,79817,70861,55282,55382,46051,61489,52641,45633,47626,54072,63425,60726,72141,68314,75986,91861,84030,105533,105146,124927,138561,144209,145359,156416,166641,188385,191270,207040,205187,225993,218059,223598,229833,245317,236380,256426,248481,258770,248646,257145,245944,234927,238714,230354,232079,216900,213678,207989,187826,179368,165690,153962,143912,145702,127007,119854,117200,94667,100642,76374,78236,64578,68120,49751,46726,55823,53437,40765,45874,49578,45311,55926,55260,76746,80269,76127,92563,90522,111679,125173,125542,130759,142485,159113,176059,188866,187116,205039,208465,213989,217317,224292,244832,248687,240665,255628,257736,247819,247744,241091,248924,236758,226987,235472,225546,220493,204187,203520,182952,178713,178675,160126,153929,142969,129000,127352,119307};
    private int[] query_1_cosine_50_min = {249499,241948,237417,252376,237681,234786,225321,221111,205315,186846,177192,167499,160846,134181,128504,124008,98233,89887,79067,83429,72901,53010,63819,57273,52551,41885,47525,44298,66326,64463,64731,74182,88144,104948,109503,127842,130477,144021,165054,161547,186435,188397,209411,223095,227558,226261,233594,238827,254342,249808,257041,245620,255938,236722,230327,224132,226859,205017,212194,191606,189671,167932,165610,144559,124834,121210,106875,104182,86244,82003,77087,59522,55489,48040,44298,43912,56943,50940,57778,70243,63765,86524,79545,98968,102902,123821,122367,135552,159917,171628,171666,187904,200975,204159,220177,222764,245278,247561,239899,250553,240523,251564,252933,239311,228842,223387,221557,219010,211547,189020,185941,168425,153355,136723,124652,127328,114755,91977,94071,85387,66917,60661,50299,56960,46192,40385,55359,54373,60602,57778,72618,69382,84069,104301,107096,123027,134683,143512,164533,178719};
    private int[] query_1_cosine_40_min = {249499,241505,235664,248499,230952,224595,211203,202768,182634,159912,146291,133117,123665,95061,88464,84199,59909,54369,47704,57557,53803,41872,61691,65031,70861,71174,87958,95757,128402,136450,145632,162722,182788,203930,210859,229454,230117,239401,253880,241577,255534,244588,250934,248453,235563,216070,204742,191249,188385,166240,157041,130765,128178,98345,83918,72520,73061,52174,63506,50260,58770,50425,64225,61738,62671,81401,90674,112365,119085,139256,157988,162796,179368,190298,202288,214622,237056,236899,245861,256642,244667,258189,238393,241651,226381,225433,199884,187231,184539,168533,140765,129683,116491,95017,88502,71152,76746,65483,47935,52573,40523,53584,60969,57233,60310,71775,89882,109868,127063,130799,155039,165330,177977,188402,202169,228940,238234,234660,252919,257052,247819,247060,238382,242919,226305,211095,213349,196631,184481,161052,153519,126635,116910,112484,90895,83218,72520,60691,63148,61212};
    private int[] query_1_cosine_30_min = {249499,240551,231913,240300,216964,203885,183326,167821,141280,113367,96291,81847,73665,49106,49428,54910,42996,52115,61908,89412,103802,109739,146344,164584,182664,191884,213650,222058,250658,249908,245633,244893,243241,239432,218994,208744,180117,160753,148322,111907,105534,78906,74927,67998,56847,45360,48149,54495,76582,83683,107040,115507,148627,154197,173598,193230,220876,222176,249966,246843,258770,247008,250685,231740,210486,202112,180354,168217,139534,123998,107989,80239,67565,53544,45695,43912,58340,56444,69854,90960,94666,128519,132835,163003,176381,204722,208019,222733,244992,250704,240765,243141,238747,221318,214194,191863,188549,165036,132588,120440,90523,85439,75173,54979,43397,42486,50846,63913,77063,79529,105039,118785,136623,153455,174292,208229,224246,226461,249168,256098,247819,246106,234631,234720,212317,190385,185472,161684,143127,114507,103520,75365,66910,66529,51859,53929,55607,58437,77352,93067};
    private int[] query_1_cosine_20_min = {249499,237842,221460,218177,180952,153885,121523,98590,70831,49163,46291,53655,73665,81682,116341,154909,171712,202248,223711,251431,253803,235746,237698,212910,182664,141885,115835,82378,78402,56988,45633,51973,70985,99752,121179,158743,180117,209079,239676,237914,255534,240925,236730,218131,185563,145360,115062,87071,76582,55491,57041,51303,78178,84966,111795,143230,184864,200053,239513,244134,258770,244299,240232,209617,174474,152111,118551,98986,69085,59794,57989,52047,67565,86120,112608,143911,187056,206577,231657,252979,244667,254526,224189,211329,176381,154722,110204,83053,72736,57784,40765,50221,66491,81638,116379,141862,188549,213362,223942,246447,240523,247458,236976,205112,172113,142485,117759,96489,77063,51337,55040,54581,66174,84224,112489,158229,188234,204338,238715,253389,247819,243397,224178,212597,176305,140384,123669,92453,72678,50303,53520,47173,66910,99105,118772,153928,184323,208570,239155,255086};
    private int[] query_1_cosine_10_min = {249499,223638,171460,128497,69149,53885,71523,126467,182634,225170,246291,229662,185468,109559,66341,54910,59909,112568,173711,237227,253803,221542,187698,123230,70861,41885,65835,110255,190205,232995,245633,227980,182788,127629,71179,58744,68314,119399,189676,223710,255534,226721,186730,128451,73760,45360,65062,114948,188385,231498,257041,227310,189981,112843,61795,43231,73061,110373,189513,229930,258770,230095,190232,119937,62671,52112,68551,126863,180888,235801,257989,228054,179368,113997,62608,43912,75253,116897,181657,238775,244667,240322,174189,121649,64578,54723,60204,110930,184539,233791,240765,226228,178294,109515,66379,41863,76746,123682,173942,232243,240523,233254,186976,115432,60310,42486,67759,124366,188866,227344,255040,230588,177977,112101,62489,58230,76431,114658,188715,239185,247819,229193,174178,122917,64502,40385,73669,120330,184481,226310,253520,223180,178713,126982,68772,53929,72520,118890,189155,240882};

    private int[] query_1_cosine = query_1_cosine_60_min;
    private int[] query_1_random = {158020,149708,149042,142595,133424,127985,128880,137208,141313,139451,134868,127442,128513,136929,144683,138406,136109,144486,149910,154642,153558,143687,144768,147127,137901,132549,135713,132384,123372,119046,123769,127615,120295,124056,123141,128875,138448,146114,154328,150149,157389,164835,164593,163290,156120,153541,145579,151891,154255,144839,149808,159635,163130,162686,163160,166508,167956,167857,166825,168007,163264,165963,157365,161113,166768,174913,173284,180939,180050,172969,175552,172671,171318,166110,172574,174732,168349,173511,167473,166567,175114,179601,169849,161062,159557,153204,151317,159794,165178,156576,159907,152516,151548,148115,149985,158507,153310,146271,142180,148860,151827,153661,153264,145828,155653,151213,142556,136496,132479,123104,117563,112122,111773,117137,116804,125474,117029,108440,118195,127573,120928,121638,112598,106991,108477,101507,96750,93770,90523,94500,94879,92169,99645,108878,113166,115024,122445,119635,128014,128232};
    private int[] query_1_increasing = {8958,5191,8876,13331,15501,8795,16901,21846,25323,24215,33748,31049,29948,32298,37628,43478,37396,30728,33072,39076,46559,43811,49388,53398,53456,55787,48936,50643,57239,54911,59978,64015,74876,83202,75736,85312,91325,89278,95701,93935,100033,94086,101041,93144,97970,102502,102844,96715,89833,95639,100436,103913,104854,102380,99085,93167,102025,109235,119011,114986,109201,115078,122584,119354,121496,117341,109922,118966,117800,127218,125683,129059,131288,132088,133404,139504,147667,157556,167312,168986,172067,164795,164010,174678,185095,182110,176184,172760,168442,170615,170826,166456,161055,155718,148825,156450,149606,158373,159034,159949,169795,180566,186387,178612,177081,171402,167717,165486,164607,172621,166626,163288,163807,155808,160461,153954,164608,175350,181154,174654,167240,163806,160575,153032,156627,165418,175693,181270,173544,181817,176497,183455,186142,187517,180646,178100,176912,178977,174744,171427};
    private int[] query_1_decreasing = {235731,228884,236569,228776,231371,236551,231568,225753,231439,237599,245611,253863,249193,239868,237163,245400,237214,244933,237687,230031,235255,237925,238220,228895,224188,229170,230140,229671,221491,218180,211591,212276,214779,218407,214092,207891,214769,221369,218042,217601,207429,214474,222466,214191,207032,200605,191480,198458,199243,188844,178584,181793,172111,166025,163298,163311,158637,162420,162058,160483,152084,154681,158982,150975,152777,158779,159728,160630,149750,144031,151130,141925,131273,121021,120359,113735,105777,105344,106751,100034,102024,100370,93123,99057,96625,102324,108697,116842,124078,129424,131116,125515,133752,131131,132889,132570,126177,115106,114688,113097,119646,110879,115359,119649,119719,110077,112188,103345,100917,95294,87676,76872,85422,81447,81984,84482,81106,89418,81061,86791,83905,80866,76022,71602,65816,72007,65433,70119,69221,71170,70868,71569,77944,73768,81609,84146,74404,75270,74159,82103};

    private int[] query_3_cosine_60_min = {68821,66993,66474,67951,66620,67681,64027,72838,66036,58813,64137,55708,51039,57104,53513,49657,56102,49740,39008,48351,40500,44924,42906,30668,36308,19559,22498,17469,30524,32864,27982,16571,19680,31868,17599,30191,34169,28944,41070,29918,33777,31066,41466,53699,43745,43586,52709,61129,66967,50271,61325,63079,72612,75695,75977,67292,77078,77578,71028,68657,71735,77545,64504,77098,66793,70542,66124,67304,64103,61827,60352,50402,57361,62046,49207,53588,40191,40594,45762,36137,33989,26679,40970,28374,22107,19005,17259,22159,27716,16409,33803,15984,32436,29701,27842,37233,35639,24040,30614,34153,29485,34186,32403,37876,39365,46345,46165,47945,55846,54740,55333,69120,74044,67318,76495,77646,79493,65280,65939,83011,70604,65093,74961,80346,78419,61671,78925,71749,64653,64948,72432,69178,48806,56074,59687,57979,53908,40636,48239,41801};
    private int[] query_3_cosine_50_min = {68821,66932,66235,67419,65689,66256,62026,70195,62703,54763,59362,50224,44883,50337,46215,41931,48071,41542,30798,40295,32774,37711,36390,25032,31731,16210,20534,17031,31733,35820,32756,23210,28198,42249,29793,44116,49710,45953,59368,49297,54003,51879,62587,74832,64583,63812,72003,79176,83456,64905,73826,73187,80098,80361,77659,65867,72464,69737,59970,54438,54460,57366,41620,51752,39270,41166,35254,35330,31439,28908,27626,18326,26391,32634,21791,28588,18002,21577,30243,24398,26263,23149,41763,33557,31688,32930,35413,44366,53739,45957,66528,51492,70285,69413,68905,79109,77772,65863,71557,73650,66986,69157,64343,66318,63886,66571,61776,58683,61516,55216,50559,59110,58885,47170,51585,48270,46010,28108,25550,39923,25378,18322,27263,32355,30778,15021,33897,28956,24680,28346,39706,40785,25145,37481,46429,50253,51837,44264,57534,56654};
    private int[] query_3_cosine_40_min = {68821,66822,65797,66450,64007,63708,58496,65609,57033,48029,51637,41629,35588,40557,36205,31979,38490,32662,22957,33827,28000,34926,35858,26971,36308,23532,30642,29896,47252,53817,52981,45345,51859,66994,55132,69519,74620,69798,81575,69305,71278,65927,72968,81172,66584,61264,64790,67281,66967,44013,48826,44474,48158,45767,41057,27964,34014,31526,22798,19101,21735,27989,16274,31046,23729,31214,31204,37376,39649,43222,47851,44144,57361,68198,61288,71265,63030,68067,77264,70998,71489,66066,81475,69228,62558,58333,54792,57285,59895,45183,58803,36937,49164,42128,35986,41206,35639,20343,23566,24155,16986,19662,16352,20798,21753,28668,28857,31398,40395,40661,42833,58336,65041,60089,70964,73673,76880,63779,65262,82840,70604,64922,74284,78845,75806,57698,73394,64520,55650,54164,59931,55099,33355,39527,42379,40301,36296,23558,32188,27277};
    private int[] query_3_cosine_30_min = {68821,66583,64859,64400,60510,58531,51527,56873,46694,36393,39137,28811,23088,29068,26446,24657,34262,32099,26508,41791,40499,51893,57021,51860,64259,53709,62065,61471,77816,82181,77982,65888,66972,75870,57166,64342,62120,50136,55185,36887,33778,24506,28966,36058,21905,18587,25642,33093,39016,23374,36325,40659,53270,59730,63477,58141,70968,74027,69413,68247,71735,77135,62889,73547,60683,61392,53624,51339,44761,39407,35352,23505,29410,34010,22140,28588,18351,22953,33262,29577,33988,33648,55085,49566,50058,53155,56826,66161,75008,65726,83803,65301,79728,73703,67409,71384,63590,45232,44729,41122,29486,27626,19903,20235,17525,21346,19098,19909,27895,27843,30333,46700,54702,51353,63995,68495,73383,61729,64324,82601,70604,64683,73346,76795,72309,52521,66425,55784,45311,42528,47432,42281,20855,28038,32620,32979,32068,22995,35739,35241};
    private int[] query_3_cosine_20_min = {68821,65906,62246,58869,51507,46031,36076,39565,29082,20342,26637,21763,23088,37212,43174,49656,66441,69632,66959,82296,78000,83395,79860,63941,64259,41210,37611,26551,34752,33951,27982,17658,23908,40950,32712,51841,62120,62217,78024,68389,71278,65011,69417,73591,54084,43587,42370,41237,39016,16326,23826,24608,35658,42422,48026,45641,61965,68496,66800,67570,71735,76458,60276,68016,51680,48891,38173,34031,27149,23356,22852,16457,29410,42154,38868,53587,50530,60486,73713,70082,71489,65150,77924,61647,50058,40655,32372,31241,31944,17496,33803,17071,36664,38783,42955,58883,63590,57313,67568,72624,66986,68131,60354,57768,49704,46345,35826,28053,27895,20795,17834,30649,37090,34045,48544,55995,64380,56198,61711,81924,70604,64006,70733,71264,63306,40020,50974,38476,27699,26477,34932,35233,20855,36182,49348,57978,64247,60528,76190,75746};
    private int[] query_3_cosine_10_min = {68821,62355,49746,36449,23556,21031,23576,46534,57033,64344,76637,65765,51039,44181,30674,24657,38490,47212,54459,78745,78000,79844,67360,41521,36308,16210,25111,33520,62703,77953,77982,61660,51859,47919,20212,26842,34169,39797,65524,64838,71278,61460,56917,51171,26133,18587,29870,48206,66967,60328,73826,68610,63609,49391,35526,20642,34014,46076,54300,64019,71735,72907,47776,45596,23729,23892,25673,41000,55100,67358,72852,60459,57361,49123,26368,28588,22579,38066,61213,66531,71489,61599,65424,39227,22107,15656,19872,38210,59895,61498,83803,61073,64615,45752,30455,33884,35639,34893,55068,69073,66986,64580,47854,35348,21753,21346,23326,35022,55846,64797,67834,74651,65041,41014,36044,30996,36429,33778,49211,78373,70604,60455,58233,48844,35355,15021,38474,45445,55650,70479,84932,79235,48806,43151,36848,32979,36296,38108,63690,72195};

    private int[] query_3_cosine = query_3_cosine_60_min;
    private int[] query_3_random = {42871,39557,38941,39251,39487,39099,36443,40229,38116,29242,21050,13482,14206,17207,25951,28261,31596,28800,37803,30848,37630,32849,30192,26805,30703,24315,32067,25016,29718,38313,30010,35743,34479,26965,29684,22795,29995,27401,18453,19638,15401,22880,25464,17451,24443,22932,18340,15032,16188,11259,5828,13574,8709,10916,16602,11793,14602,5403,3106,6823,755,4786,2427,11129,8281,10004,4824,9878,856,9901,18123,27776,33583,29755,27168,35066,39816,47570,52335,44786,38084,43107,44513,52790,56499,57614,50427,47923,48393,43662,43434,44233,40606,31138,32728,41324,46333,45896,43854,40427,33417,28840,38507,29688,21342,23576,16159,13487,5840,14108,7160,3565,6097,13354,6965,8223,5800,6256,16075,9890,8039,10016,10876,5097,13575,11669,16798,11718,11761,10694,4181,4502,10482,8237,4176,13565,17720,25259,34001,32769};
    private int[] query_3_increasing = {3617,2706,5145,4115,7148,9694,13045,13838,16446,17176,19556,20397,20419,19385,20098,17710,19093,17602,19953,23103,21355,23756,21979,19498,19433,22030,21038,18708,19754,18297,19755,20058,20746,20803,23781,25943,28675,28991,29617,29213,32451,32826,32045,35218,35937,34668,37451,38402,38508,39161,38557,37141,35593,38866,39721,38380,41528,41926,39579,40229,43502,44367,46989,48740,46879,50187,49003,52266,49946,51188,50925,49090,48530,50659,48336,47052,49781,52137,54480,54459,54925,53359,55531,54950,56347,56147,54589,56156,55582,56486,58000,59327,56859,55922,58881,60178,60636,62227,60355,58511,57874,58758,61911,60587,63675,61777,62174,64180,62044,65383,63816,63499,66569,69864,72736,70373,72074,70530,73121,76520,75736,77974,78369,77477,78819,81377,83232,83399,83702,82228,81541,84708,85266,87591,85186,84592,84624,85198,82773,83870};
    private int[] query_3_decreasing = {84020,86785,87139,85154,82662,78982,80489,77663,78081,78574,81279,81120,82849,83410,84960,86570,83824,84121,83603,83292,81903,83655,85404,85182,81942,80916,78915,79896,76525,78056,74649,75237,74370,71558,70843,71202,71131,69021,66859,64210,62310,59985,59838,56876,55446,55762,54090,52456,52674,55120,57887,54575,51591,47893,47753,46095,46297,47664,48620,47800,47048,48218,49969,47970,47031,43540,45318,43105,45504,48173,48866,48261,48127,49992,46766,43032,44306,44053,43614,40175,37041,37618,37910,37865,36630,34330,35163,37775,39171,36560,38575,37224,37260,34172,30416,26736,25530,24154,20708,20931,20965,20073,19106,15445,17655,17646,13864,12401,13404,11491,12115,14712,13627,10406,7043,9232,5941,4021,2152,3897,5489,6472,4699,6381,6981,5345,4815,3260,5153,5058,5021,1581,1776,3701,6653,4153,6732,7826,6671,7984};

    private int[] query_11_cosine_60_min = {45776,42764,37216,44832,44100,47803,33129,35632,42959,48387,38792,44904,32739,27560,35004,28321,24087,19038,19628,27227,14917,21071,17892,22966,24489,16136,7604,16566,15869,22487,18500,16243,12952,15051,6950,14156,16888,10525,26479,18782,28649,19432,16612,33601,38055,35150,25421,27820,30088,26728,33715,38267,43545,45637,44249,49578,52564,49667,48194,54084,47446,50892,45333,44351,45110,51379,45132,33380,31956,37351,31148,37787,33835,35390,22057,30340,23525,34673,31193,28729,32309,20116,20458,17885,24806,16749,25827,23783,10670,8122,19066,10945,10870,15050,22114,11939,13363,19221,29444,22597,32240,30308,31766,30895,31416,27093,39120,34834,42589,42515,33446,30139,34356,34289,33609,42163,48548,41200,39914,49640,50129,49330,34727,51636,46796,38844,49868,32797,35424,36586,31321,37008,28218,38090,22082,20462,37694,33770,20468,33581};
    private int[] query_11_cosine_50_min = {45776,42728,37072,44513,43541,46948,31928,34046,40960,45957,35927,41613,29045,23500,30626,23685,19268,14119,14702,22394,10281,16743,13982,19585,21743,14127,6426,16303,16595,24260,21364,20226,18063,21279,14267,22511,26213,20731,37457,30409,40785,31920,29285,46281,50557,47285,36998,38648,39981,35508,41216,44332,48037,48436,45258,48723,49795,44963,41559,45553,37081,38785,31602,29144,28596,33753,26610,14195,12358,17600,11512,18541,15253,17743,5608,15340,10211,23263,21882,21686,27673,17998,20933,20995,30555,25104,36720,37107,26284,25850,38701,32249,33580,38877,46752,37065,38643,44315,54009,46295,54741,51291,50930,47960,46128,39229,48487,41277,45991,42800,30582,24133,25261,22200,18663,24537,28458,18897,15680,23788,22993,21268,6108,22842,18211,10854,22851,7121,11441,14625,11685,19972,14021,26934,14128,15826,36451,35947,26045,42493};
    private int[] query_11_cosine_40_min = {45776,42662,36809,43932,42532,45419,29810,31294,37558,41917,31292,36456,23468,17632,24620,17714,13519,8791,9998,18513,7417,15072,13663,20748,24489,18520,12491,24022,25906,35058,33500,33507,32260,36126,29470,37753,41159,35038,50781,42414,51150,40349,35513,50085,51758,45756,32670,31511,30088,22973,26216,27104,28873,27680,23297,25981,26725,22036,19256,24351,17446,21159,16395,16720,19271,27782,24180,15423,17284,26188,23647,34032,33835,39081,29306,40946,37228,51157,50094,49646,54809,43748,44760,42398,49077,40346,48347,44858,29978,25386,34066,23516,20907,22506,27001,14323,13363,17003,25215,16598,24741,21594,22136,20648,20848,16487,28736,24906,33318,34067,25946,23669,28955,29951,30290,39779,46980,40300,39507,49538,50129,49228,34320,50736,45228,36460,46549,28459,30023,30116,23820,28560,18947,28162,11698,9855,27126,23523,10838,24867};
    private int[] query_11_cosine_30_min = {45776,42519,36247,42702,40433,42313,25629,26052,31355,34935,23792,28766,15968,10738,18764,13321,10982,8453,12128,23292,14916,25252,26361,35681,41260,36626,31344,42967,44245,52077,48500,45833,41328,41452,30690,34647,33659,23240,34948,22963,28650,15497,9112,23016,24950,20150,9181,10998,13317,10590,18715,24815,31941,36057,36749,44087,48897,47537,47225,53839,47446,50647,44364,42221,41443,45889,37632,23800,20352,23899,16148,21649,17064,18568,5817,15340,10420,24088,23693,24794,32308,24297,28927,30600,41577,37239,49567,50184,39046,37712,49066,40535,39246,41451,45854,32430,30134,31936,37913,26778,32241,26373,24266,20310,18311,12094,22880,18012,25818,26377,18446,16687,22752,24709,26109,36672,44881,39070,38945,49395,50129,49085,33758,49506,43129,33354,42368,23217,23820,23134,16321,20870,11447,21268,5842,5462,24589,23185,12968,29646};
    private int[] query_11_cosine_20_min = {45776,42112,34679,39383,35032,34813,16358,15668,20787,25305,16292,24537,15968,15625,28801,28320,30290,30973,36399,47594,37417,44153,40064,42930,41260,29127,16672,22015,18406,23139,18500,16895,15489,20500,16018,27146,33659,30489,48651,41864,51150,39799,33383,45536,44258,35150,19218,15885,13317,6361,11216,15185,21373,25673,27478,36587,43496,44218,45657,53432,47446,50240,42796,38902,36042,38388,28361,13416,9784,14269,8648,17420,17064,23455,15854,30339,29728,46608,47964,49096,54809,43198,42630,37849,41577,29739,34895,29232,13207,8774,19066,11597,13407,20499,31182,24929,30134,39185,51616,45679,54741,50675,48537,42830,37619,27093,32917,22899,25818,22148,10947,7057,12184,14325,16838,29172,39480,35751,37377,48988,50129,48678,32190,46187,37728,25853,33097,12833,13252,13504,8821,16641,11447,26155,15879,20461,43897,45705,37239,53948};
    private int[] query_11_cosine_10_min = {45776,39982,27179,25931,18261,19813,8858,19849,37558,51706,46292,50938,32739,19806,21301,13321,13519,17521,28899,45464,37417,42023,32564,29478,24489,14127,9172,26196,35177,49540,48500,43296,32260,24681,8518,12147,16888,17037,41151,39734,51150,37669,25883,32084,27487,20150,11718,20066,30088,32762,41216,41586,38144,29854,19978,21588,26725,30766,38157,51302,47446,48110,35296,25450,19271,23389,20861,17597,26555,40670,38648,43821,33835,27636,8354,15340,12957,33156,40464,46966,54809,41068,35130,24397,24806,14740,27395,33413,29978,35175,49066,37998,30178,24680,23682,9930,13363,25733,44116,43549,54741,48545,41037,29378,20848,12094,25417,27080,42589,48549,40947,33458,28955,18506,9338,14173,22709,22299,29877,46858,50129,46548,24690,32735,20957,10854,25597,17014,30023,39905,38821,43042,28218,30336,8379,5462,27126,32253,29739,51818};

    private int[] query_11_cosine = query_11_cosine_60_min;
    private int[] query_11_random = {28705,37567,36304,28118,27536,33616,37893,30628,39555,31622,25838,19605,18791,15578,24699,20057,26742,27185,35042,36482,45809,45424,38054,39880,30165,25463,24958,19311,17957,23516,14188,19866,17818,11434,12500,6292,7422,12820,15240,17511,16904,17375,18221,20142,18541,16107,10579,17398,14325,21996,18248,19523,12319,16591,7399,4078,1061,5718,10603,5901,3478,1062,8574,17629,21430,23116,15555,9141,3980,4246,4420,2755,2290,6918,16877,14193,12372,9739,1855,11449,16652,14331,24002,16232,20417,24628,20591,24995,19399,21436,16413,24372,31852,27623,28958,33798,29336,25088,18839,20762,17828,16277,16305,16976,24113,30335,37024,46881,43939,48516,39311,29693,34421,27896,18019,12468,11979,13391,12331,11685,13809,22752,24831,17480,24716,32376,24990,34139,39985,30965,31256,23361,13745,8783,1187,3956,8991,13124,15924,22115};
    private int[] query_11_increasing = {4617,11067,7161,3929,852,5307,7095,8807,2718,1697,4964,482,3827,6565,11267,10832,13358,6678,5384,7510,3093,2487,8050,8005,7171,5683,1197,1368,3563,3153,331,164,2922,6819,9571,11576,6987,7596,6096,10417,15005,18103,20846,24271,28101,31136,30865,28294,31228,32563,37794,43449,43897,47641,45074,45435,48875,53472,53280,48310,54988,56409,56187,57838,59913,61813,60749,59971,55404,58082,53126,59230,55855,51799,58244,53674,48901,53875,50305,52989,57563,58584,56339,58944,59616,63575,60530,66948,66230,69369,64687,59780,63292,67199,71016,69341,65585,64577,61261,56759,55604,51803,47243,53361,53155,55468,50726,55260,58540,61329,61519,57488,61150,60503,58266,59797,64127,63234,59408,63567,67091,63230,60049,55691,52404,57081,60355,63593,61209,62742,67623,68538,68011,70878,75311,79449,84540,86556,89316,94599};
    private int[] query_11_decreasing = {150636,145117,142436,138036,134476,136838,137683,142438,143380,144672,148352,141244,136970,131889,136619,132695,126950,123387,127431,122421,121848,117091,115227,116310,117206,121447,119197,119665,124691,126401,126388,130503,127174,124963,129391,131197,132196,136390,130170,128717,126398,125578,121592,126374,123310,118270,116532,114927,114695,107833,110983,111403,111633,109945,109603,113910,117232,116853,117921,119010,111919,114330,115208,119857,118436,123662,126028,125281,125147,125317,126807,129832,134396,134041,136611,136845,135593,138433,139299,139735,140944,141136,140242,140625,138745,136350,130270,130940,124887,124947,120354,123616,117904,113186,112147,116603,111910,111333,105432,109570,110300,113834,116536,111634,105788,108360,101260,104864,108048,106491,103445,107020,108440,103529,98886,100345,103366,101608,102554,105087,98405,102682,97075,96949,91370,84288,77462,76675,73175,70904,72586,76861,74154,74466,68635,68453,69554,70251,71577,67687};

    private final int rate;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public BidPersonGeneratorKafkaOld(int srcRate) {
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
        return getExperimentRate(time, query, load_pattern, -1);
    }

    public int getExperimentRate(long time, String query, String load_pattern, int cosine_period){
        int elapsed_minutes = (int)Math.floor((double) ((System.currentTimeMillis() - time) / 60000));
        int limit = 1000;
        if (query.equals("query-1") && load_pattern.equals("cosine") && elapsed_minutes < 140){
            switch(cosine_period) {
                case 10:
                    limit = query_1_cosine_10_min[elapsed_minutes];
                    break;
                case 20:
                    limit = query_1_cosine_20_min[elapsed_minutes];
                    break;
                case 30:
                    limit = query_1_cosine_30_min[elapsed_minutes];
                    break;
                case 40:
                    limit = query_1_cosine_40_min[elapsed_minutes];
                    break;
                case 50:
                    limit = query_1_cosine_50_min[elapsed_minutes];
                    break;
                case 60:
                    limit = query_1_cosine_60_min[elapsed_minutes];
                    break;
                default:
                    limit = query_1_cosine[elapsed_minutes];
                    break;
            }
        } else if (query.equals("query-1") && load_pattern.equals("random") && elapsed_minutes < 140){
            limit = query_1_random[elapsed_minutes];
        } else if (query.equals("query-1") && load_pattern.equals("increasing") && elapsed_minutes < 140){
            limit = query_1_increasing[elapsed_minutes];
        } else if (query.equals("query-1") && load_pattern.equals("decreasing") && elapsed_minutes < 140){
            limit = query_1_decreasing[elapsed_minutes];
        } else if (query.equals("query-3") && load_pattern.equals("cosine") && elapsed_minutes < 140){
            switch(cosine_period) {
                case 10:
                    limit = query_3_cosine_10_min[elapsed_minutes];
                    break;
                case 20:
                    limit = query_3_cosine_20_min[elapsed_minutes];
                    break;
                case 30:
                    limit = query_3_cosine_30_min[elapsed_minutes];
                    break;
                case 40:
                    limit = query_3_cosine_40_min[elapsed_minutes];
                    break;
                case 50:
                    limit = query_3_cosine_50_min[elapsed_minutes];
                    break;
                case 60:
                    limit = query_3_cosine_60_min[elapsed_minutes];
                    break;
                default:
                    limit = query_3_cosine[elapsed_minutes];
                    break;
            }
        } else if (query.equals("query-3") && load_pattern.equals("random") && elapsed_minutes < 140){
            limit = query_3_random[elapsed_minutes];
        } else if (query.equals("query-3") && load_pattern.equals("increasing") && elapsed_minutes < 140){
            limit = query_3_increasing[elapsed_minutes];
        } else if (query.equals("query-3") && load_pattern.equals("decreasing") && elapsed_minutes < 140){
            limit = query_3_decreasing[elapsed_minutes];
        } else if (query.equals("query-11") && load_pattern.equals("cosine") && elapsed_minutes < 140){
            switch(cosine_period) {
                case 10:
                    limit = query_11_cosine_10_min[elapsed_minutes];
                    break;
                case 20:
                    limit = query_11_cosine_20_min[elapsed_minutes];
                    break;
                case 30:
                    limit = query_11_cosine_30_min[elapsed_minutes];
                    break;
                case 40:
                    limit = query_11_cosine_40_min[elapsed_minutes];
                    break;
                case 50:
                    limit = query_11_cosine_50_min[elapsed_minutes];
                    break;
                case 60:
                    limit = query_11_cosine_60_min[elapsed_minutes];
                    break;
                default:
                    limit = query_11_cosine[elapsed_minutes];
                    break;
            }
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
        int cosine_period = params.getInt("period", 60);
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
                current_rate = getExperimentRate(start_time, "query-1", "cosine", cosine_period);
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
                current_rate = getExperimentRate(start_time, "query-3", "cosine", cosine_period);
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
                current_rate = getExperimentRate(start_time, "query-11", "cosine", cosine_period);
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
        BidPersonGeneratorKafkaOld test = new BidPersonGeneratorKafkaOld(10000);
        try{
            test.run(args);
            Thread.sleep(1200000);
        }
        catch (Exception e){
            System.out.println(e);
        }
    }

}