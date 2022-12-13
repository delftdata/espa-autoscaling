package ch.ethz.systems.strymon.ds2.flink.nexmark.sources;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class TestBidPersonAuctionSourceParallelManager {

    @Test
    public void testGetRatePerEpoch() {
        BidPersonAuctionSourceParallelManager sourceManager = new BidPersonAuctionSourceParallelManager(null, 0, true,
                true, true, 4);
        sourceManager.epochDurationMs = 100;
        assertEquals(sourceManager.getRatePerEpoch(1000), 100);
    }

    @Test
    public void testGetAmountOfEpochs() {
        BidPersonAuctionSourceParallelManager sourceManager = new BidPersonAuctionSourceParallelManager(null, 0, true,
                true, true, 4);
        sourceManager.epochDurationMs = 100;
        assertEquals(10, sourceManager.getAmountOfEpochs(999));
        assertEquals(10, sourceManager.getAmountOfEpochs(1000));
        assertEquals(11, sourceManager.getAmountOfEpochs(1001));

        sourceManager.epochDurationMs = 57;
        assertEquals(18, sourceManager.getAmountOfEpochs(1000));

    }
}
