package ch.ethz.systems.strymon.ds2.flink.nexmark.sources.LoadPattern;

import org.apache.flink.api.java.tuple.Tuple2;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/***
 * Generate a cosinus load pattern.
 * Load Pattern is based on the following Python code:
 *   cosine_period = 60
 *   if query == "query-1":
 *       amplitude = 100000
 *      yshift = 150000
 *   elif query == "query-3":
 *       amplitude = 25000
 *       yshift = 50000
 *   elif query == "query-11":
 *       amplitude = 15000
 *       yshift = 30000
 *   values = []
 *   indices = []
 *   for i in range(0, time):
 *       period = (2 * math.pi / cosine_period)
 *       val = yshift + amplitude * math.cos(period * i)
 *       val += random.randrange(-10000, 10000)
 *       values.append(val)
 *       indices.append(i)
 *   values = [int(val) for val in values]
 *   values = [-1*val if val < 0 else val for val in values]
 *   return indices, values
 */
public class CosineLoadPattern extends LoadPattern {

    int meanInputRate;
    int maximumDivergence;
    int cosinePeriod;

    /**
     * Generate Cosinus Load pattern using default values dependign on query.
     * @param query query to generate default values from.
     */
    public CosineLoadPattern(int query, int loadPatternPeriod) {
        super(query, loadPatternPeriod);
        this.setDefaultValues();
    }


    /**
     * Generate Cosinus load pattern using custom values.
     * @param query Query to generate load pattern from. Only used for graph description.
     * @param loadPatternPeriod Experiment length (minutes) to generate load for
     * @param cosinePeriod Time a full cosinus period takes (minutes)
     * @param maximumDivergence Maximum input rate to diverge from mean
     * @param meanInputRate Average input rate
     */
    public CosineLoadPattern(int query, int loadPatternPeriod, int cosinePeriod, int maximumDivergence, int meanInputRate) {
        super(query, loadPatternPeriod);
        this.cosinePeriod = cosinePeriod;
        this.meanInputRate = meanInputRate;
        this.maximumDivergence = maximumDivergence;
    }

    /**
     * Spike up configuration
     *  spikeChance = the chance for an upspike to occur.
     *  spikeMaximumPeriod = the maximum amount of time an upspike can take place (between 1 and spikeUpPeriod)
     *  spikeMaximumInputRate = the minimum value for the decrease
     *  spikeMinimumInputRate = the maximum value for the decrease
     */
    double spikeChance = 0.05;            // default = 0.05
    int spikeMaximumPeriod = 1;           // default = 1
    double spikeMaximumInputRate = 0;     // default = 0
    double spikeMinimumInputRate = 0;     // default = 0

    /**
     * Set the chance for an spike event to occur in a range of (0, 1)
     * @param spikeChance Chance for a spike event to occur
     */
    public void setSpikeChance(double spikeChance) {
        this.spikeChance = spikeChance;
    }

    /**
     * Set the maximum period a spike event can occur for randomly selected from range (1, spikeMaximumPeriod)
     * @param spikeMaximumPeriod Maximum period a spike event can take occur for
     */
    public void setSpikeMaximumPeriod(int spikeMaximumPeriod) {
        this.spikeMaximumPeriod = spikeMaximumPeriod;
    }

    public void setSpikeMaximumInputRateRange(int spikeMaximumInputRate) {
        this.spikeMaximumInputRate = spikeMaximumInputRate;
    }

    public void setSpikeMinimumInputRateRange(int spikeMinimumInputRate) {
        this.spikeMinimumInputRate = spikeMinimumInputRate;

    }


//    /**
//     * Spike up configuration
//     *  spikeUpChance = the chance for an upspike to occur.
//     *  spikeUpMaximumPeriod = the maximum amount of time an upspike can take place (between 1 and spikeUpPeriod)
//     *  spikeUpMaximumInputRate = the minimum value for the decrease
//     *  spikeUpMinimumInputRate = the maximum value for the decrease
//     */
//    double spikeUpChance = 0.05;            // default = 0.05
//    int spikeUpMaximumPeriod = 1;           // default = 1
//    double spikeUpMaximumInputRate = 0;     // default = 0
//    double spikeUpMinimumInputRate = 0;     // default = spikeUpMaximumInputRate / 2
//
//    /**
//     * Set the chance for an upspike event to occur in a range of (0, 1)
//     * @param spikeUpChance Chance for a upspike event to occur
//     */
//    public void setSpikeUpChance(double spikeUpChance) {
//        this.spikeUpChance = spikeUpChance;
//    }
//
//    /**
//     * Set the maximum period a spike up event can occur for randomly selected from range (1, spikeUpMaximumPeriod)
//     * @param spikeUpMaximumPeriod Maximum period a spike event can take occur for
//     */
//    public void setSpikeUpMaximumPeriod(int spikeUpMaximumPeriod) {
//        this.spikeUpMaximumPeriod = spikeUpMaximumPeriod;
//    }
//
//    /**
//     * Set SpikeInputRateRange with the decrease being between (spikeUpRate, spikeUpRate / 2)
//     * @param spikeUpRate Maximum spike size in terms of input rate.
//     */
//    public void setSpikeUpInputRateRange(int spikeUpRate) {
//        this.setSpikeUpInputRateRange((int) (spikeUpRate / 2), spikeUpRate);
//    }
//
//    /**
//     * Set SpikeInputRate Range with the decrease being between (spikeUpMinimumRate and spikeUpMaximumRate)
//     * @param spikeUpMinimumRate Minimum value the input rate can decrease with
//     * @param spikeUpMaximumRate Maximum value the input rate can decrease with
//     * An additional check makes place to ensure spikeUpMinimum < spikeUpMaximum
//     */
//    public void setSpikeUpInputRateRange(int spikeUpMinimumRate, int spikeUpMaximumRate) {
//        this.spikeUpMinimumInputRate = Math.min(spikeUpMinimumRate, spikeUpMaximumRate);
//        this.spikeUpMaximumInputRate = Math.max(spikeUpMinimumRate, spikeUpMaximumRate);
//    }

//    /**
//     * Spike down configuration
//     *  spikeDownChance = the chance for a downspike to occur.
//     *  spikeDownMaximumPeriod = the maximum amount of time a downspike can take place (between 1 and spikeDownPeriod)
//     *  spikeDownMaximumInputRate = the minimum value for the decrease
//     *  spikeDownMinimumInputRate = the maximum value for the decrease
//     *  An additional check mekes sure Minimum < Maximum.
//     */
//    // Spike down configurations
//    double spikeDownChance = 0.05;            // default = 0.05
//    int spikeDownMaximumPeriod = 1;           // default = 1
//    double spikeDownMaximumInputRate = 0;     // default = 0
//    double spikeDownMinimumInputRate = 0;     // default = spikeDownMaximumInputRate / 2
//
//    /**
//     * Set the chance for a downspike event to occur in a range of (0, 1)
//     * @param spikeDownChance Chance for a downspike event to occur
//     */
//    public void setSpikeDownChance(double spikeDownChance) {
//        this.spikeDownChance = spikeDownChance;
//    }
//
//    /**
//     * Set the maximum period a spike event can occur for randomly selected from range (1, spikeDownMaximumPeriod)
//     * @param spikeDownMaximumPeriod Maximum period a spike event can take occur for
//     */
//    public void setSpikeDownMaximumPeriod(int spikeDownMaximumPeriod) {
//        this.spikeDownMaximumPeriod = spikeDownMaximumPeriod;
//    }
//
//    /**
//     * Set SpikeInputRateRange with the decrease being between (spikeDownRate, spikeDownRate / 2)
//     * @param spikeDownRate Maximum spike size in terms of input rate.
//     */
//    public void setSpikeDownInputRateRange(int spikeDownRate) {
//        this.setSpikeDownInputRateRange(spikeDownRate, (int) (spikeDownRate / 2));
//
//    }
//
//    /**
//     * Set SpikeInputRate Range with the decrease being between (spikeDownMinimumRate and spikeDownMaximumRate)
//     * @param spikeDownMinimumRate Minimum value the input rate can decrease with
//     * @param spikeDownMaximumRate Maximum value the input rate can decrease with
//     * An additional check makes place to ensure spikeDownMinimum < spikeDownMaximum
//     */
//    public void setSpikeDownInputRateRange(int spikeDownMinimumRate, int spikeDownMaximumRate) {
//        this.spikeDownMinimumInputRate = Math.min(spikeDownMinimumRate, spikeDownMaximumRate);
//        this.spikeDownMaximumInputRate = Math.max(spikeDownMinimumRate, spikeDownMaximumRate);
//    }


    /**
     * Set the default values based on this.query.
     */
    @Override
    public void setDefaultValues() {
        // Spike settings are set in value constructors
        this.cosinePeriod = 60;
        switch (this.getQuery()) {
            case 1:
                this.meanInputRate = 150000;
                this.maximumDivergence = 100000;
                break;
            case 3:
                this.meanInputRate = 50000;
                this.maximumDivergence = 25000;
                break;
            case 11:
                this.meanInputRate = 30000;
                this.maximumDivergence = 15000;
                break;
            default:
                System.out.println("Error: query " + this.getQuery() + " not recognized.");
        }
    }

    @Override
    public String getLoadPatternTitle() {
        return "Cosine pattern ("+ this.getSeed() + ")\n" +
                "Query " + this.getQuery() +
                " - Period " + this.cosinePeriod +
                " - Mean " + this.meanInputRate +
                " - Div " + this.maximumDivergence;
    }

    /**
     * Generate Cosinus pattern
     * @return Tuple with a list of indices and a list of indexes.
     */
    @Override
    public Tuple2<List<Integer>, List<Integer>> getLoadPattern() {
        Random random = this.getRandomClass();
        List<Integer> values = new ArrayList<>();
        List<Integer> indices = new ArrayList<>();

        int remainingSpikePeriods = 0;

        for (int i = 0; i < this.getLoadPatternPeriod(); i++) {
            double period = (2 * Math.PI / this.cosinePeriod);
            double value = this.meanInputRate + this.maximumDivergence * Math.cos(period * i);
            value += random.nextDouble() * 20000 - 10000;

            // If not spiking
            if (remainingSpikePeriods <= 0) {
                // CHeck whether a new spiking event can occur
                if (random.nextDouble() <= this.spikeChance) {
                    // Set spike periods between (1, this.spikeMaximumPeriod)
                    // Next round spiking will start
                    remainingSpikePeriods = (int) (random.nextDouble() * this.spikeMaximumPeriod);
                }
            } else {
                // If spiking
                remainingSpikePeriods -= 1;
                int additionalSpikeInputRate = (int) (
                        random.nextDouble()
                        * (this.spikeMaximumInputRate - this.spikeMinimumInputRate)
                        - this.spikeMinimumInputRate
                );
                value += additionalSpikeInputRate;
            }


            value = Math.abs(value);
            values.add((int) value);
            indices.add(i);
        }
        return new Tuple2<>(indices, values);
    }
}