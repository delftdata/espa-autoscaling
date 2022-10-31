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
    public CosineLoadPattern(int query) {
        super(query, 140);
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
     * Set the default values based on this.query.
     */
    @Override
    public void setDefaultValues() {
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
        for (int i = 0; i < this.getLoadPatternPeriod(); i++) {
            double period = (2 * Math.PI / this.cosinePeriod);
            double value = this.meanInputRate + this.maximumDivergence * Math.cos(period * i);
            value += random.nextDouble() * 20000 - 10000;
            value = Math.abs(value);
            values.add((int) value);
            indices.add(i);
        }
        return new Tuple2<>(indices, values);
    }
}