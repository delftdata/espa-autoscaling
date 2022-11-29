import ch.ethz.systems.strymon.ds2.flink.nexmark.sources.BidPersonGeneratorKafka;
import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class TestBidPersonGeneratorKafka {
    private final BidPersonGeneratorKafka bidPersonGeneratorKafka;

    public TestBidPersonGeneratorKafka() {
        this.bidPersonGeneratorKafka = new BidPersonGeneratorKafka();
    }

    private void getTimestampUsforEventTest(long epochStartTimeMs, long epochDurationMs, long eventsPerEpoch,
                                            long firstEventCurrentEpoch, long eventNumber, long expectedTimestamp) {
        long assignedTimestamp = this.bidPersonGeneratorKafka.getTimestampUsforEvent(
                epochStartTimeMs,
                epochDurationMs,
                eventsPerEpoch,
                firstEventCurrentEpoch,
                eventNumber
        );
        assertEquals(expectedTimestamp, assignedTimestamp);
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
}