package ch.ethz.systems.strymon.ds2.flink.nexmark.sources.LoadPattern;

import org.apache.flink.api.java.tuple.Tuple2;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

/**
 * Create an increasing load pattern.
 * The implementation is based on the following code:
 *   if query == "query-1":
 *      magnitude = 240000
 *   elif query == "query-3":
 *       magnitude = 75000
 *   elif query == "query-11":
 *       magnitude = 150000
 *   initial_val = magnitude
 *   values = []
 *   indices = []
 *   val = 2000
 *  for i in range(0, time):
 *       val += random.randrange(int(-initial_val * (1 / 30)), int(initial_val * (1 / 22)))
 *       values.append(val)
 *       indices.append(i)
 *   values = [int(val) for val in values]
 *   values = [-1*val if val < 0 else val for val in values]
 *   return indices, values
 */
public class IncreaseLoadPattern extends LoadPattern {
    int magnitude;
    int startValue;

    /**
     * Constructor for loadPattern. Configurations are based on the provided query.
     * @param query Query to generate the load pattern for.
     */
    public IncreaseLoadPattern(int query) {
        super(query, 140);

        this.setDefaultValues();
    }

    /**
     * Set default values of class based on this.query.
     */
    @Override
    public void setDefaultValues() {
        this.startValue = 2000;
        switch (this.getQuery()) {
            case 1:
                this.magnitude = 240000;
                break;
            case 3:
                this.magnitude = 75000;
                break;
            case 11:
                this.magnitude = 150000;
                break;
            default:
                System.out.println("Error: query " + this.getQuery() + " not recognized.");
        }
    }

    @Override
    public String getLoadPatternTitle() {
        return "Decrease pattern ("+ this.getSeed() + ")\n" +
                "Query " + this.getQuery() +
                " - Start Value " + this.startValue;
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

        int value = this.startValue;
        for (int i = 0; i < this.getLoadPatternPeriod(); i++) {
            int minRange = -1 * this.magnitude / 30;
            int maxRange = this.magnitude / 22;
            value += random.nextDouble() * (maxRange - minRange) + minRange;;
            value = Math.abs(value);
            values.add(value);
            indices.add(i);
        }
        System.out.println(Arrays.toString(values.toArray()));
        System.out.println(values.size());
        System.out.println(indices.size());
        return new Tuple2<>(indices, values);
    }
}
