package ch.ethz.systems.strymon.ds2.flink.nexmark.sources;
import org.junit.Test;

import java.util.*;

import static org.junit.Assert.*;

public class TestBidPersonAuctionSourceFunction {
    private final BidPersonAuctionSourceFunction timestampUsTestBidPersonAuctionSourceFunction;

    public TestBidPersonAuctionSourceFunction() {
        this.timestampUsTestBidPersonAuctionSourceFunction = new BidPersonAuctionSourceFunction(null, 1000);
    }


    private List<Long> getNonDuplicateListCopy(List<Long> list) {
        return this.getNonDuplicateListCopy(list, false);
    }
    private List<Long> getNonDuplicateListCopy(List<Long> list, boolean sort) {
        List<Long> result = new ArrayList<>(new HashSet<>(list));
        if (sort) {
            Collections.sort(result);
        }
        return result;
    }

    private void getTimestampUsforEventTest(long epochStartTimeMs, long epochDurationMs, long eventsPerEpoch,
                                            long firstEventCurrentEpoch, long eventNumber, long expectedTimestamp) {
        long actualTimestamp =this.timestampUsTestBidPersonAuctionSourceFunction.getTimestampUsforEvent(epochStartTimeMs,
                epochDurationMs, eventsPerEpoch, firstEventCurrentEpoch, eventNumber);
        assertEquals(actualTimestamp, expectedTimestamp);
    }

    @Test
    public void getTimestampUsForEventTests() {
        this.getTimestampUsforEventTest(
                5600,
                100,
                1_000_000,
                56_000_000,
                56_129_190,
                5_612_919
        );
        this.getTimestampUsforEventTest(
                5600,
                100,
                1_000_000,
                56_000_000,
                56_129_199,
                5_612_919
        );
        this.getTimestampUsforEventTest(
                5600,
                100,
                1_000_000,
                56_000_000,
                56_129_200,
                5_612_920
        );
        this.getTimestampUsforEventTest(
                5600,
                100,
                1_000_000,
                56_000_000,
                56_129_200,
                5_612_920
        );
    }
    @Test
    public void getTimestampUsForEventTestsDifferentStartTime() {
        this.getTimestampUsforEventTest(
                1000,
                100,
                1_000_000,
                56_000_000,
                56_129_190,
                1_012_919
        );
    }

    /**
     * Check whether the provided list does not contain any duplicate values.
     * @param list List to check for duplicates.
     */
    void testListContainsNoDuplicates(List<Long> list) {
        assertEquals(this.getNonDuplicateListCopy(list).size(), list.size());
    }

    /**
     * Test whether all event numbers are present (should be ordered from 0 -> list.length)
     * @param eventNumbers Eventnumbers to check.
     */
    void testAllEventNumbersArePresent(List<Long> eventNumbers) {
        for (int i = 0; i < eventNumbers.size(); i++){
            assertEquals((long) eventNumbers.get(i), (long) i);
        }
    }

    /**
     * Test whether the timestamps always increment with a constant factor.
     * @param timestamps Timestamps to check.
     * @param expectedIncrement Constant factor we expect the timestamps to increment by.
     */
    void testTimestampsIncrementsAreConstant(List<Long> timestamps, long expectedIncrement) {
        long previous = timestamps.get(0);
        for (int i = 1; i < timestamps.size(); i++) {
            long next = timestamps.get(i);
            long difference = next - previous;
            assertEquals(difference, expectedIncrement);
            previous = next;
        }
    }

    /**
     * Test whether the timestampIncrements are increasing.
     * @param timestamps Timestamps to check.
     */
    void testTimestampsIncrementsAreIncreasing(List<Long> timestamps) {
        this.testTimestampsIncrementsAreChanging(timestamps, true);
    }

    /**
     * Test whether the timestampIncrements are decreasing.
     * @param timestamps Timestamps to check.
     */
    void testTimestampsIncrementsAreDecreasing(List<Long> timestamps) {
        this.testTimestampsIncrementsAreChanging(timestamps, false);
    }

    /**
     * Check whether the increase in values in the list is in the list of allowedDifferences.
     * @param list List to check the increases for.
     * @param allowedDifferences List of allowed differences of the list.
     */
    void testValueIncreaseIsInList(List<Long> list, List<Long> allowedDifferences) {
        long previousItem = -1;
        for (long item: list) {
            if (previousItem >= 0) {
                long difference = item - previousItem;
                assertTrue(allowedDifferences.contains(difference));
            }
            previousItem = item;
        }
    }

    /***
     * Test whether the increase of the timestamps is increasing / decreasing depending on the boolean 'increasing'.
     * We add a roundingLeniency, to allow for difference in results caused by rounding.
     * @param timestamps Timestamps to check
     * @param increasing Whether the increase of timestamps should be increasing (true) or decreasing (false)
     */
    public void testTimestampsIncrementsAreChanging(List<Long> timestamps, boolean increasing) {

        long roundingLeniency = 1;
        long previousDifference = increasing ? Long.MIN_VALUE + roundingLeniency : Long.MAX_VALUE - roundingLeniency;
        long previousTimestamp = timestamps.get(0);
        boolean changed = false;
        for (int i = 1; i < timestamps.size(); i++) {
            long nextTimestamp = timestamps.get(i);
            long difference = nextTimestamp - previousTimestamp;
            if (increasing) {
                assertTrue(difference >= previousDifference - roundingLeniency);
            } else {
                assertTrue(difference <= previousDifference + roundingLeniency);
            }
            previousTimestamp = nextTimestamp;

            if (previousDifference != difference) {
                if (previousDifference != Long.MIN_VALUE && previousDifference != Long.MAX_VALUE) {
                    changed = true;
                }
                previousDifference = difference;
            }
        }
        assertTrue(changed);
    }

    @Test
    public void testGenerationUniqueTimestampsIncreasingInputRate() {
        /**
         * Check whether the timestamp difference is indeed decreasing when we increase the input rate per epoch.
         */
        int epochDurationMs = 10;
        BidPersonAuctionSourceFunction bidPersonAuctionSourceFunction = new BidPersonAuctionSourceFunction(null, epochDurationMs);
        List<Long> eventNumbers = new ArrayList<>();
        List<Long> timestamps = new ArrayList<>();
        for (int epoch = 0; epoch < 100; epoch++) {
            int epochInputRate = 3000 + epoch * 100;
            bidPersonAuctionSourceFunction.setNextEpochSettings(epochInputRate);
            for (int i = 0; i < epochInputRate; i++ ) {
                long eventNumber = bidPersonAuctionSourceFunction.getNextEventNumber();
                eventNumbers.add(eventNumber);
                long timestamp = bidPersonAuctionSourceFunction.getTimestampUsforEvent(eventNumber);
                timestamps.add(timestamp);
            }
        }
        this.testListContainsNoDuplicates(eventNumbers);
        this.testAllEventNumbersArePresent(eventNumbers);
        this.testTimestampsIncrementsAreDecreasing(timestamps);
    }

    @Test
    public void testGenerationUniqueTimestampsDecreasingInputRate() {
        /**
         * Check whether the timestamp difference is indeed increasing when we decrease the input rate per epoch.
         */
        int epochDurationMs = 10;
        BidPersonAuctionSourceFunction bidPersonAuctionSourceFunction = new BidPersonAuctionSourceFunction(null, epochDurationMs);

        List<Long> eventNumbers = new ArrayList<>();
        List<Long> timestamps = new ArrayList<>();
        for (int epoch = 0; epoch < 100; epoch++) {
            int epochInputRate = 13000 - (epoch * 100);
            bidPersonAuctionSourceFunction.setNextEpochSettings(epochInputRate);
            for (int i = 0; i < epochInputRate; i++ ) {
                long eventNumber = bidPersonAuctionSourceFunction.getNextEventNumber();
                eventNumbers.add(eventNumber);
                long timestamp = bidPersonAuctionSourceFunction.getTimestampUsforEvent(eventNumber);
                timestamps.add(timestamp);
            }
        }
        this.testListContainsNoDuplicates(eventNumbers);
        this.testAllEventNumbersArePresent(eventNumbers);
        this.testTimestampsIncrementsAreIncreasing(timestamps);
    }

    @Test
    public void testGenerationUniqueTimestampsMinimalTimestampSteps() {
        /**
         * Test whether all eventNumbers and Timestamps are present when we set the amount of records/s exactly to
         * 1,000,000 records. In this case, every timestamp should differ exactly 1us from each other.
         */
        int epochDurationMs = 10;
        BidPersonAuctionSourceFunction bidPersonAuctionSourceFunction = new BidPersonAuctionSourceFunction(null, epochDurationMs);
        List<Long> eventNumbers = new ArrayList<>();
        List<Long> timestamps = new ArrayList<>();
        for (int epoch = 0; epoch < 100; epoch++) {
            int epochInputRate = 10000;
            bidPersonAuctionSourceFunction.setNextEpochSettings(epochInputRate);
            for (int i = 0; i < epochInputRate; i++ ) {
                long eventNumber = bidPersonAuctionSourceFunction.getNextEventNumber();
                eventNumbers.add(eventNumber);
                long timestamp = bidPersonAuctionSourceFunction.getTimestampUsforEvent(eventNumber);
                timestamps.add(timestamp);
            }
        }
        this.testListContainsNoDuplicates(eventNumbers);
        this.testAllEventNumbersArePresent(eventNumbers);
        this.testListContainsNoDuplicates(timestamps);
        this.testTimestampsIncrementsAreConstant(timestamps, 1);
    }

    @Test
    public void testGenerationUniqueTimestampsDuplicateTimestampSteps() {
        /**
         * Test whether the timestamps are overlapping correctly when producing more than 1.000.000 records per second.
         * In this case, duplicate timestamps should be produced without any of the timestamps missing, while the
         * event ID's should remain the same.
         */
        int epochDurationMs = 10;
        BidPersonAuctionSourceFunction bidPersonAuctionSourceFunction = new BidPersonAuctionSourceFunction(null, epochDurationMs);
        List<Long> eventNumbers = new ArrayList<>();
        List<Long> timestamps = new ArrayList<>();
        for (int epoch = 0; epoch < 100; epoch++) {
            int epochInputRate = 20000;
            bidPersonAuctionSourceFunction.setNextEpochSettings(epochInputRate);
            for (int i = 0; i < epochInputRate; i++ ) {
                long eventNumber = bidPersonAuctionSourceFunction.getNextEventNumber();
                eventNumbers.add(eventNumber);
                long timestamp = bidPersonAuctionSourceFunction.getTimestampUsforEvent(eventNumber);
                timestamps.add(timestamp);
            }
        }
        this.testListContainsNoDuplicates(eventNumbers);
        this.testAllEventNumbersArePresent(eventNumbers);
        List<Long> uniqueTimestamps = this.getNonDuplicateListCopy(timestamps);
        Collections.sort(uniqueTimestamps);
        assertEquals(uniqueTimestamps.size(), timestamps.size() / 2);
        this.testTimestampsIncrementsAreConstant(uniqueTimestamps, 1);
    }

    @Test
    public void testGenerationUnfinishedInputRateGeneration() {
        /**
         * Test what happens if only half the input-rate is acutally generated.
         * Expected: increase is normal until end of epoch is reached. Then the input rate and timestamps are set to 0
         * in the next epoch.
         */
        int epochDurationMs = 10;
        BidPersonAuctionSourceFunction bidPersonAuctionSourceFunction = new BidPersonAuctionSourceFunction(null, epochDurationMs);
        List<Long> eventNumbers = new ArrayList<>();
        List<Long> timestamps = new ArrayList<>();
        for (int epoch = 0; epoch < 100; epoch++) {
            int epochInputRate = 100;
            bidPersonAuctionSourceFunction.setNextEpochSettings(epochInputRate);
            for (int i = 0; i < epochInputRate / 2; i++ ) {
                long eventNumber = bidPersonAuctionSourceFunction.getNextEventNumber();
                eventNumbers.add(eventNumber);
                long timestamp = bidPersonAuctionSourceFunction.getTimestampUsforEvent(eventNumber);
                timestamps.add(timestamp);
            }
        }

        this.testListContainsNoDuplicates(eventNumbers);
        this.testValueIncreaseIsInList(eventNumbers, new ArrayList<Long> (Arrays.asList(1L, 51L)));
        this.testValueIncreaseIsInList(timestamps, new ArrayList<Long> (Arrays.asList(100L, 5100L)));
    }
}