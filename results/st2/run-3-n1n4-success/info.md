Compared execution of experiments on two setups:
- 1n: 1 node with 64GB memory and 16 processors
- 4n: 4 nodes with 16GB memory and 4 processors
In the experiments, ds2 was wrongfully configured, resulting in wrong results.
Ran:

query 1
- dhalion_5
- ds2-original_0.33  Failed for n1 and n4 because of a misconfiguration
- ds2-updated_0.33   Failed for n1 and n4 because of a misconfiguration
- HPA_70             Failed for n1 for unknown reasons
- varga_0.5

query 3
- dhalion_5
- ds2-original       Failed for n1 and n4 becauses of a misconfiguration

query 11
- dhalion_5
- ds2-original       Failed for n1 and n4 becauses of a misconfiguration
