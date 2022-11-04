# Dhalion implementation

## Pseudocode original Dhalion operator



### Overprovisioning detection
1. If no backpressure exists in the topology
2. If the number of pending packets is almost zero
If scale down results in backpressure, action is reverted and blacklisted.

``` 
if no backpressure exists:
    if for all instances of operator, the average number of pending packets is almost 0:
        scale down with {underprovisioning system}
if after scaling down, backpressure is observed:
    undo action and blacklist action
```

### Underprovisioning detection
1. If backpressure exists that is caused by underprovisioning
2. Find bottleneck causing backpressure
3.Calculate scale-up factor by:
   percentage of time instances spend suspending input tata 
   / amount of time backpressure was not observed
 
``` 
If backpressure exists:
    If backpressure cannot be contributed to slow instances or skew (it can't:
        Find bottleneck causing the backpressure
        Scale up bottleneck
```       

Operations to implement:
1. Detect backpressure
2. Find operator causing backpressure
3. Calcualte scale-up factor


## Implementation proposal




### Summary (notes)

Symptom detection phase
Every 300 seconds, metrics are gathered and symptoms are identified.
- Pending packets detector
    Monitor stream manager queue of each instance
    Detect whether queue sizes are similar or different    
    This provides insights into potential system bottlenecks
- Backpressure detector
    Evaluate whether topology experiences backpressure
    Indicate which operator is the cause of the backpressure
- Processing rate skew detector
    Investigate whether skew in processing rates is observed at each topology stage
    
Diagnosis Generation Phase
- Resource overprovsiioning diagnoser: 
    Take PendingPackets Detector and Backpressure Detector
    1. Does backpressure exist in the topology?
    2. If so, do nothing
    3. If not, check if average number of pending packets is almost zero
    4. Examine every operator and indicate which one is likely overprovisioned
- Resource underprovisioning diagnoser
    1. If backpressure is in the system
    2. If backpressure cannot be contributed to a slow instance or skew
    3. Determine backpressure is caused by limited resources being attributed to bottleneck
- Resolution phase

Action phase
- Scale down resolver: scale down operators
    Configurable scale down factor
    When resoucre voerprovisioning is provoked.
- Scale up resovler: scale up operators
    Scale up operators that initiated the backpressure

- Bolt scale up resolver`