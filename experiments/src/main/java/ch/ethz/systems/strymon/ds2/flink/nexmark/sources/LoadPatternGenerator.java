package ch.ethz.systems.strymon.ds2.flink.nexmark.sources;

import ch.ethz.systems.strymon.ds2.flink.nexmark.sources.plotting.LoadPatternChart_AWT;
import org.apache.flink.api.java.tuple.Tuple2;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class LoadPatternGenerator {

    /**
     * def cosine_plot(time, query):
     * cosine_period = 60
     * if query == "query-1":
     * amplitude = 100000
     * yshift = 150000
     * <p>
     * elif query == "query-3":
     * amplitude = 25000
     * yshift = 50000
     * <p>
     * elif query == "query-11":
     * amplitude = 15000
     * yshift = 30000
     * <p>
     * values = []
     * indices = []
     * for i in range(0, time):
     * period = (2 * math.pi / cosine_period)
     * val = yshift + amplitude * math.cos(period * i)
     * val += random.randrange(-10000, 10000)
     * values.append(val)
     * indices.append(i)
     * values = [int(val) for val in values]
     * values = [-1*val if val < 0 else val for val in values]
     * return indices, values
     */
    public Tuple2<List<Integer>, List<Integer>> getCosinePlot(
            int time,
            String query,
            Random random) {
        int cosinePeriod = 60;
        int amplitude = 0;
        int yShift = 0;
        switch (query) {
            case "query-1":
                amplitude = 100000;
                yShift = 150000;
                break;
            case "query-3":
                amplitude = 25000;
                yShift = 50000;
                break;
            case "query-11":
                amplitude = 15000;
                yShift = 30000;
                break;
        }
        List<Integer> values = new ArrayList<>();
        List<Integer> indices = new ArrayList<>();
        for (int i = 0; i < time; i++) {
            double period = (2 * Math.PI / cosinePeriod);
            double value = yShift + amplitude * Math.cos(period * i);
            value += random.nextDouble() * 20000 - 10000;
            value = Math.abs(value);
            values.add((int) value);
            indices.add(i);
        }
        return new Tuple2<>(indices, values);
    }

    /***
     def random_walk(time, query):
     if query == "query-1":
     val = 150000
     elif query == "query-3":
     val = 50000
     elif query == "query-11":
     val = 30000

     values = []
     indices = []
     for i in range(0, time):
     val += random.randrange(-10000, 10000)
     values.append(val)
     indices.append(i)
     values = [int(val) for val in values]
     values = [-1*val if val < 0 else val for val in values]
     return indices, values
     ***/
    public Tuple2<List<Integer>, List<Integer>> getRandomWalk(
            int time,
            String query,
            Random random) {
        int startValue = 0;
        switch (query) {
            case "query-1":
                startValue = 150000;
                break;
            case "query-3":
                startValue = 50000;
                break;
            case "query-11":
                startValue = 30000;
                break;
        }

        List<Integer> values = new ArrayList<>();
        List<Integer> indices = new ArrayList<>();

        int value = startValue;
        for (int i = 0; i < time; i++) {
            value += random.nextDouble() * 20000 - 10000;
            value = Math.abs(value);
            values.add(value);
            indices.add(i);
        }
        return new Tuple2<>(indices, values);
    }

    /***
     def increasing(time, query):
     if query == "query-1":
     magnitude = 240000
     elif query == "query-3":
     magnitude = 75000
     elif query == "query-11":
     magnitude = 150000
     initial_val = magnitude
     values = []
     indices = []
     val = 2000
     for i in range(0, time):
     val += random.randrange(int(-initial_val * (1 / 30)), int(initial_val * (1 / 22)))
     values.append(val)
     indices.append(i)
     values = [int(val) for val in values]
     values = [-1*val if val < 0 else val for val in values]
     return indices, values
     ***/
    public Tuple2<List<Integer>, List<Integer>> increasing(
            int time,
            String query,
            Random random) {
        int magnitude = 0;
        switch (query) {
            case "query-1":
                magnitude = 240000;
                break;
            case "query-3":
                magnitude = 75000;
                break;
            case "query-11":
                magnitude = 150000;
                break;
        }
        int startValue = 2000;

        List<Integer> values = new ArrayList<>();
        List<Integer> indices = new ArrayList<>();

        int value = startValue;
        for (int i = 0; i < time; i++) {
            int minRange = -1 * magnitude / 30;
            int maxRange = magnitude / 22;
            value += random.nextDouble() * (minRange * maxRange) - minRange;
            value = Math.abs(value);
            values.add(value);
            indices.add(i);
        }
        return new Tuple2<>(indices, values);
    }


    /***
     def decreasing(time, query):
     if query == "query-1":
     val = 240000
     elif query == "query-3":
     val = 80000
     elif query == "query-11":
     val = 150000
     initial_val = val
     values = []
     indices = []
     val += 2000
     for i in range(0, time):
     val += random.randrange(int(-initial_val * (1 / 21)), int(initial_val * (1/28)))
     values.append(val)
     indices.append(i)
     values = [int(val) for val in values]
     values = [-1*val if val < 0 else val for val in values]
     return indices, values
     ***/
    public Tuple2<List<Integer>, List<Integer>> decreasing(
            int time,
            String query,
            Random random) {
        int startValue = 0;
        switch (query) {
            case "query-1":
                startValue = 240000;
                break;
            case "query-3":
                startValue = 80000;
                break;
            case "query-11":
                startValue = 150000;
                break;
        }

        List<Integer> values = new ArrayList<>();
        List<Integer> indices = new ArrayList<>();

        int value = startValue + 2000;
        for (int i = 0; i < time; i++) {
            int minRange = -1 * startValue / 21;
            int maxRange = startValue / 28;
            value -= random.nextDouble() * (minRange * maxRange) - minRange;
            value = Math.abs(value);
            values.add(value);
            indices.add(i);
        }
        return new Tuple2<>(indices, values);
    }


    Tuple2<List<Integer>, List<Integer>>  getLoadPattern() {
        Random random = new Random(1066);
        return this.getCosinePlot(140, "query 1", random);
    }

    /**
     * Generate a load pattern and display it as chart
     */
    public void plotLoadPattern() {
        Tuple2<List<Integer>, List<Integer>> loadPattern = this.getLoadPattern();
        List<Integer> indices = loadPattern.f0;
        List<Integer> values = loadPattern.f1;
        String title = "Load Pattern: " + "Cosinus";

        LoadPatternChart_AWT loadPatternChart = new LoadPatternChart_AWT(
                title, title,
                indices,
                values,
                "Input rate",
                "Input rate",
                "Time (min)"
        );
        loadPatternChart.pack();
        loadPatternChart.setVisible(true);
    }

    public static void main( String[ ] args ) throws Exception {
        LoadPatternGenerator loadPatternGenerator = new LoadPatternGenerator();
        loadPatternGenerator.plotLoadPattern();
    }

}
