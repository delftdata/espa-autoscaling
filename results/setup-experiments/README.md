# Results of setup
Goal of experiment: investigate difference between setup with 1 node and 4 nodes




# Reults of redone
Goal of experiments: redo the experiments performed in original thesis

Query 1
- | Dhalion      | 1   - 6a-parallel | 5   - 3-n1n4-success | 10  - 6a-parallel |
- | ds2-original | 0   - 6a-parallel | 33  - 6a-parallel    | 66  - 6a-parallel |
- | ds2-updated  | 0   - 6a-parallel | 33  - 6a-parallel    | 66  - 6a-parallel |
- | HPA          | 50  - 6d-parallel | 70  - 6d-parallel	| 90  - 6d-parallel	|
- | varga1       | 0.3 - 6a-parallel | 0.5 - 3-n1n4-success | 0.7 - 6a-parallel |
- | varga2       | 0.3 - 6a-parallel | 0.5 - 6a-parallel    | 0.7 - 6a-parallel |

Query 3
- | Dhalion      | 1   - 6a-parallel | 5   - 3-n1n4-success | 10  - 6a-parallel |
- | ds2-original | 0   - 6a-parallel | 33  - 6a-parallel    | 66  - 6c-parallel |
- | ds2-updated  | 0   - 6c-parallel | 33  - 6c-parallel    | 66  - 6c-parallel |
- | HPA          | 50  - 6e-parallel | 70  - 6e-parallel	| 90  - 6a-parallel |
- | varga1       | 0.3 - 6a-parallel | 0.5 - 6b-parallel    | 0.7 - 6b-parallel |
- | varga2       | 0.3 - 6b-parallel | 0.5 - 6b-parallel    | 0.7 - 6c-parallel |

Query 11 
- | Dhalion      | 1   - 6c-parallel | 5   - 3-n1n4-success | 10  - 6c-parallel |
- | ds2-original | 0   - 6d-parallel | 33  - 6d-parallel    | 66  - 6d-parallel |
- | ds2-updated  | 0   - 6d-parallel | 33  - 6d-parallel    | 66  - 6d-parallel |
- | HPA          | 50  - 6e-parallel | 70  - 6e-parallel	| 90  - 6e-parallel	|
- | varga1       | 0.3 - 6d-parallel | 0.5 - 6d-parallel    | 0.7 - 6d-parallel |
- | varga2       | 0.3 - 6d-parallel | 0.5 - 6d-parallel    | 0.7 - 6d-parallel |


#Runs
### run-0parallel-random-resources-short
Test run aimed at testing the parallel experiment setup.
Time was set to 5 minutes to test the correctness of the scripts.
Results were not usefull due to wrongly set resource capacity.

### run-1-parallel-random-resources
Test run aimed at testing our parallel experiment setup. 
Results were not useful due to wrongly set resource capacity.

### run-2-n1n4-failed
Run aimed at comparing setup with a single node and four nodes with equal total memory and CPUs.
Results were not useful due to wrong fileformat.

### run-3-n1n4-success
Run aimed at comparing setup with a single node and four nodes with equal total memory and CPUs.
The few results collected after running this experiment for some time provide insight into the possibility to only use a single node to simplify the deployment procedure.

### run-4-short-fail
First run with correct resources and a single node but only 15 minutes wait time.
Run resulted in a testrun of every experiment, but results are not usefull due to wrong time setting.

### run-5-parallel-fail
First run with correct resources and a single node.
Run failed due to wrongly set file formats, resulting in wrong script execution.

### run-6a-parallel
Run with correct resources and single node. Experiment ran for 2 days, collecting resuls for the first query and partly the thrid query.
After investigating results, HPA appears to fail in execution. Because of this the execution of this experiment is delayed.
Experiment was stopped due to some problems in disk useage. The execution was remained in run-6b-parallel with disk assignment of 20gb.

### run-6b-parallel
Continued execution of run-6a-parallel only with explicit disk assignment of 20gb to each node.
The experiment performed 4 correct runs after failing to clean up a persitent volume due to an improperly closing pod.
hooping this was just a temporary failure, after clean-up, execution was resumed in run-6c-parallel.

### run-6c-parallel
After cleaning up the persistent problem resulting in improper experiment execution in run-6b-parallel, run-6c-parallel was started.
Run-6c-parallel was eventually ended due to a repeating problem of the Kafka brokers taking up too much disk space.
After investigation, the problem was solved and run-6d-parallel was started to resume exeuction.

### run-6d-parallel
Run-6d-parallel finished executing on 05/10/2022 and therby finished the remaining experiments excluding HPA. 
Just as run-6a-parallel, run-6b-parallel and run-6c-parallel this run was performed with a parallelsim of 1 experiment a time.

### run-6e-parallel
As previous runs excluded the HPA autoscaler due to technical reasons, this run soly executed the experiments involving the autoscaler.
Experiments were performed with parallelism 3. For completeness, q3_HPA_90 was repeated in this run.