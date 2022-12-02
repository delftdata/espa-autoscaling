package ch.ethz.systems.strymon.ds2.flink.nexmark.sources;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class TestBidPersonAuctionSourceParallelFunction {

    @Test
    public void testEpochEventChunkSize() {
        BidPersonAuctionSourceParallelFunction sourceFunction = new BidPersonAuctionSourceParallelFunction(null, 0, true,
                true, true, 4, 1);

        assertEquals(sourceFunction.getEpochEventChunkSize(101), 26);
        assertEquals(sourceFunction.getEpochEventChunkSize(100), 25);
        assertEquals(sourceFunction.getEpochEventChunkSize(99), 25);
        assertEquals(sourceFunction.getEpochEventChunkSize(98), 25);
        assertEquals(sourceFunction.getEpochEventChunkSize(97), 25);
        assertEquals(sourceFunction.getEpochEventChunkSize(96), 24);
        assertEquals(sourceFunction.getEpochEventChunkSize(3), 1);

    }

    @Test
    public void testFistEventIndex() {
        BidPersonAuctionSourceParallelFunction sourceFunction = new BidPersonAuctionSourceParallelFunction(null, 0, true,
                true, true, 1, 0);

        assertEquals(sourceFunction.getEpochEventChunkSize(1), 1);
        assertEquals(sourceFunction.getFirstEventIndex(1), 0);

        assertEquals(sourceFunction.getEpochEventChunkSize(96), 96);
        assertEquals(sourceFunction.getFirstEventIndex(96), 0);

        assertEquals(sourceFunction.getEpochEventChunkSize(97462), 97462);
        assertEquals(sourceFunction.getFirstEventIndex(97462), 0);
    }


    @Test
    public void getEpochChunkSizeandEventIndex_parallelism_1() {
        BidPersonAuctionSourceParallelFunction sourceFunction = new BidPersonAuctionSourceParallelFunction(null, 0, true,
                true, true, 4, 1);

        assertEquals(sourceFunction.getEpochEventChunkSize(96), 24);
        sourceFunction.parallelismIndex = 0;
        assertEquals(sourceFunction.getFirstEventIndex(96), 0);
        sourceFunction.parallelismIndex = 1;
        assertEquals(sourceFunction.getFirstEventIndex(96), 24);
        sourceFunction.parallelismIndex = 2;
        assertEquals(sourceFunction.getFirstEventIndex(96), 48);
        sourceFunction.parallelismIndex = 3;
        assertEquals(sourceFunction.getFirstEventIndex(96), 72);
    }

    @Test
    public void testEventIndexLargeTotalEvents() {
        BidPersonAuctionSourceParallelFunction sourceFunction = new BidPersonAuctionSourceParallelFunction(null, 0, true,
                true, true, 7, 1);
        assertEquals(sourceFunction.getEpochEventChunkSize(68896), 9843);
        sourceFunction.parallelismIndex = 0;
        assertEquals(sourceFunction.getFirstEventIndex(68896), 0);
        sourceFunction.parallelismIndex = 1;
        assertEquals(sourceFunction.getFirstEventIndex(68896), 9843);
        sourceFunction.parallelismIndex = 2;
        assertEquals(sourceFunction.getFirstEventIndex(68896), 9843 * 2);
        sourceFunction.parallelismIndex = 3;
        assertEquals(sourceFunction.getFirstEventIndex(68896), 9843 * 3);
        sourceFunction.parallelismIndex = 4;
        assertEquals(sourceFunction.getFirstEventIndex(68896), 9843 * 4);
        sourceFunction.parallelismIndex = 5;
        assertEquals(sourceFunction.getFirstEventIndex(68896), 9843 * 5);
        sourceFunction.parallelismIndex = 6;
        assertEquals(sourceFunction.getFirstEventIndex(68896), 9843 * 6);
    }


}
