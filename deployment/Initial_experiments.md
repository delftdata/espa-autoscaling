# Initial experiments


# Benchmarks

## Workbench resources benchmark
Doing a small benchmark, the following results were found as a relationship between the workbench input generation and its provided resources
The benchmark was done by requesting an input stream of 10,000,000 records per seconds on a 60s period with 100ms epochs.
During the benchmark, all topics were enabled. Memory was set at 20GB, as the CPU is seen as the limiting factor in input generation.

###Producing all records

Threads used | CPUs | Memory | Input rate
64 | 32 | 32GB | 2,900,000 r/s
16 | 10 | 20GB | 2,500,000 r/s
20 | 10 |  5GB | 2,250,000 r/s
16 | 8  | 20GB | 1,900,000 r/s
16 | 6  | 20GB | 1,400,000 r/s
16 | 4  | 20GB |   850,000 r/s

### Producing person and auction

Threads used | CPUs | Memory | Input rate
20 | 10 |  20GB | 850,000 r/s
20 | 10 |  5GB | 800,000 r/s
15 | 16 |  16GB | 1,000,000 r/s


### Event comparison
Records enabled     | parallelism   | CPUs  | Memory    | Input Rate
Auctions            | 15            | 16    | 8GB       | 1,000,000 r/s
Persons             | 15            | 16    | 8GB       | 1,700,000 r/s
Bids                | 15            | 16    | 8GB       | 1,800,000 r/s
Person & Auctions   | 15            | 16    | 8GB       | 1,000,000 r/s
Person & Auctions   | 31            | 16    | 8GB       | 1,000,000 r/s
Person & Auctions   | 15            | 8     | 4GB       |   600,000 r/s
Bids                | 15            | 8     | 4GB       | 2,200,000 r/s

## Initial experiments
The goal of the first experiment is to investigate the effect of the input rate on the scaling behavior of the operators.
We will do this with an initial run of HPA-CPU with the following parameters: CPU_UTILIZATION_TARGET_VALUE=0.7.
The workbench will run with the following resource assignment: 20 threads, 10 cpu, 5GB memory.

We will use the following cosine workload configurations:
| Mean | div | maximum input|
|   40k |  20k |   60k |
|   80k |  40k |  120k |
|  180k |  90k |  240k |
|  360k | 180k |  480k |


Each experiment will run for 140 minutes