package ch.ethz.systems.strymon.ds2.flink.nexmark.sources;

import org.apache.kafka.clients.producer.Producer;

import java.util.List;

public class BidPersonAuctionSourceParallelFunction extends BidPersonAuctionSourceFunction implements Runnable {
    // Parallelism status
    int parallelism;
    int parallelismIndex;

    // Thread status
    Thread thread;
    boolean running = false;

    // Epoch status
    private int amountOfEpochs;
    private int totalEventsPerEpoch;

    public BidPersonAuctionSourceParallelFunction(Producer<String, byte[]> producer, long epochDurationMs, boolean enablePersonTopic, boolean enableAuctionTopic, boolean enableBidTopic, int parallelism, int parallelismIndex) {
        super(producer, epochDurationMs, enablePersonTopic, enableAuctionTopic, enableBidTopic);
        this.parallelism = parallelism;
        this.parallelismIndex = parallelismIndex;
    }

    /**
     * Set epochStartTimeMs and EventCountSoFar to the provided variables.
     * This is used to synchronise the parallel source functions, so the timestamps and IDs generated remain consistent.
     * @param epochStartTimeMs Epoch start time.
     * @param eventsCountSoFar Events-count so far.
     */
    public void synchroniseSourceFunction(long epochStartTimeMs, long eventsCountSoFar) {
        this.epochStartTimeMs = epochStartTimeMs;
        this.eventsCountSoFar = eventsCountSoFar;
    }

    /**
     * Start a new thread. As preconditions, no thread should be running.
     * @param totalEventsPerEpoch Events that are generated in total by all generators combined per epoch.
     * @param amountOfEpochs Amount of epochs to generate events for
     */
    public void startNewThread(int totalEventsPerEpoch, int amountOfEpochs) {
        if (!running) {
            int amountOfEpochsOffset = amountOfEpochs % this.parallelism;
            this.totalEventsPerEpoch = totalEventsPerEpoch + amountOfEpochsOffset;
            this.amountOfEpochs = amountOfEpochs;

            this.running = true;
            this.thread = new Thread(this);
            this.thread.start();
        } else {
            System.out.println("Error: attempting to start generator[ " + this.parallelismIndex + "] while it is already" +
                    " running");
        }
    }

    /**
     * Stop the currently running thread. Stopping is done by interrupting the thread.
     * As precondition, a thread should be running.
     */
    public void stopThread() {
        if (this.running) {
            this.running = false;
            this.thread.interrupt();
            System.out.println("Shutting down generator[" + this.parallelismIndex + "]");
        } else {
            System.out.println("Warning: attempting to shut down generator[" + this.parallelismIndex + "] while it " +
                    "was already shutting down.");
        }
    }

    /**
     * Get the amount of events every generator has to generate.
     * @return The amoutn every generator has to generate.
     */
    int getEpochEventChunkSize(int totalEvents) {
        return (int) Math.ceil( totalEvents / (double) this.parallelism);
    }

    /**
     * Get the index of the first event the generator should generate.
     * @return The index of the first event the generator should generate
     */
    int getFirstEventIndex(int totalEvents) {
        int epochChunkSize = this.getEpochEventChunkSize(totalEvents);
        return epochChunkSize * this.parallelismIndex;
    }

    /**
     * Run function of the source generator.
     * It runs for this.amountOfEpochs * this.epochDurationMs seconds.
     * This time might increase when the load per epoch takes longer to generate than the epoch.
     * The function determines the amount of events it has to generate (total / parallelism) and the from which
     * event it should start generating ((total / parallelism) * index).
     */
    public void run() {
        for (int i = 0; (i < this.amountOfEpochs); i++) {
            long epochStartTime = System.currentTimeMillis();
            int eventChunkSize = this.getEpochEventChunkSize(this.totalEventsPerEpoch);
            int firstEventIndex = this.getFirstEventIndex(this.totalEventsPerEpoch);
            try {
                this.generatePortionOfEpochEvents(
                        this.totalEventsPerEpoch,
                        firstEventIndex,
                        eventChunkSize);
            }  catch (Exception e){
                e.printStackTrace();
            }
            long emitTime = System.currentTimeMillis() - epochStartTime;
            if (emitTime < this.epochDurationMs) {
                try {
                    Thread.sleep(this.epochDurationMs - emitTime);
                } catch (InterruptedException e) {
                    System.out.println("Generator[" + this.parallelismIndex + "] was interrupted. Stopping generator...");
                    return;
                }
            }
        }
        System.out.println("Generator[" + this.parallelismIndex + "] finished");
    }
}
