package org.apache.flink;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.Properties;
import java.util.concurrent.atomic.AtomicLong;

public class DataGen {
    private static volatile boolean sendFailmessage = false;

    public static void main(String[] args) throws Exception {
        System.out.println("Args = " + Arrays.asList(args));
        final String topic = args[0];
        final AtomicLong sleepEvery = new AtomicLong(Long.parseLong(args[1]));
        Properties props = new Properties();
        long sleep = Long.parseLong(args[6]);
        props.put("bootstrap.servers", args[2]);
        props.put("acks", "all");
        props.put("retries", 0);
        props.put("linger.ms", 1);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

        Thread producerThread =
                new Thread(
                        () -> {
                            Producer<String, String> producer = new KafkaProducer<>(props);
                            long i = 0;
                            while (true) {
                                if (sendFailmessage) {
                                    producer.send(new ProducerRecord<>(topic, "fail", "fail"));
                                    sendFailmessage = false;
                                } else {
                                    producer.send(
                                            new ProducerRecord<>(
                                                    topic, Long.toString(i), Long.toString(i++)));
                                }

                                if (i % sleepEvery.get() == 0) {
                                    System.out.println(
                                            "Sleep interval "
                                                    + sleepEvery.get()
                                                    + " Kafka produced: "
                                                    + i);
                                    try {
                                        Thread.sleep(sleep * 1000);
                                    } catch (InterruptedException e) {
                                        e.printStackTrace();
                                        break;
                                    }
                                }
                            }
                        });

        producerThread.start();

        System.out.println("Kafka Producer started.");
        long median = Long.parseLong(args[7], 10);
        long current;
        double in = -Math.PI / 2;
        int i = 0;
        double noise = Math.random();
        double period = Double.parseDouble(args[5]);

        switch (args[3]) {
            case "manual":
                BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
                while (true) {
                    System.out.println("Enter new sleep:");
                    String line = br.readLine();
                    System.out.println("Read " + line);
                    if (!line.isEmpty()) {
                        if (line.equals("fail")) {
                            sendFailmessage = true;
                        } else {
                            sleepEvery.set(Long.parseLong(line));
                        }
                    }
                }
            case "cos":
                while (true) {
                    current = median + (long) (median * Math.cos(in));
                    if (Boolean.valueOf(args[4])) {
                        current += (noise - 0.5) * 10000;
                    }
                    current += 1;
                    sleepEvery.set(current);
                    in += Math.PI / period;
                    System.out.println("At time " + (i++) + " Setting current " + current);
                    Thread.sleep(sleep * 1000L); // once per minute.
                }
            case "square":
                while (true) {
                    if (Math.cos(in) > 0) {
                        current = 10000;
                    } else {
                        current = 5000;
                    }
                    if (Boolean.valueOf(args[4])) {
                        current += (noise - 0.5) * 10000;
                    }
                    sleepEvery.set(current);
                    in += Math.PI / period;
                    System.out.println("At time " + (i++) + " Setting current " + current);
                    Thread.sleep(sleep * 1000L); // once per minute.
                }
            case "constant":
                while (true) {
                    current = median
                    sleepEvery.set(current);
                    System.out.println("At time " + (i++) + " Setting current " + current);
                    Thread.sleep(sleep * 1000L); // once per minute.
                }    

            default:
                throw new IllegalArgumentException("unexpected mode " + args[3]);
        }
    }
}
