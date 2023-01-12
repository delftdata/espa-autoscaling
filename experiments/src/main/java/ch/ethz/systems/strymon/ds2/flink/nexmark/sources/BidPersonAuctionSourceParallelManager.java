package ch.ethz.systems.strymon.ds2.flink.nexmark.sources;

import org.apache.kafka.clients.producer.Producer;

import java.util.ArrayList;
import java.util.List;

public class BidPersonAuctionSourceParallelManager {

    int parallelism;
    long epochDurationMs;
    List<BidPersonAuctionSourceParallelFunction> sourceFunctions;

    public BidPersonAuctionSourceParallelManager(String kafkaServer,
                                                 long epochDurationMs,
                                                 boolean enablePersonTopic,
                                                 boolean enableAuctionTopic,
                                                 boolean enableBidTopic,
                                                 int parallelism) {
        this.parallelism = parallelism;
        this.epochDurationMs = epochDurationMs;
        this.sourceFunctions = new ArrayList<>();
        for (int i = 0; i < this.parallelism; i++) {
            this.sourceFunctions.add(new BidPersonAuctionSourceParallelFunction(kafkaServer, epochDurationMs,
                    enablePersonTopic, enableAuctionTopic, enableBidTopic, parallelism, i));
        }
    }

    public int getRatePerEpoch(int totalRatePerSecond) {
        double epochsPerSecond = 1000d / this.epochDurationMs;
        return (int) Math.ceil(totalRatePerSecond / epochsPerSecond);
    }

    public int getAmountOfEpochs(int periodDurationMs) {
        return (int) Math.ceil(periodDurationMs / (double) this.epochDurationMs);
    }

    public void runGeneratorsForPeriod(int totalRatePerSecond, int periodDurationMs) throws InterruptedException {
        int ratePerEpoch = this.getRatePerEpoch(totalRatePerSecond);
        int amountOfEpochs = this.getAmountOfEpochs(periodDurationMs);
        for (BidPersonAuctionSourceParallelFunction sourceFunction: this.sourceFunctions) {
            sourceFunction.startNewThread(ratePerEpoch, amountOfEpochs);
        }
        Thread.sleep(periodDurationMs);
        for (BidPersonAuctionSourceParallelFunction sourceFunction: this.sourceFunctions) {
            sourceFunction.stopThread();
        }
    }
}