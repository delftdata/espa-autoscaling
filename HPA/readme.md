# HPA implementation
Implementation is based on: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/


The following information is explicitly used when implementing

'Before checking the tolerance and deciding on the final values, the control plane also considers whether any metrics are missing, and how many Pods are Ready. All Pods with a deletion timestamp set (objects with a deletion timestamp are in the process of being shut down / removed) are ignored, and all failed Pods are discarded.'

If a pod is missing or yet to become ready, it is set asside.

Readiness metrics delay: horizontal-pod-autoscaler-initial-readiness-delay (default: 30s)
- A pod is not yet ready if it's unready and transitioned to ready within a short, configurable window of time since it started.
- After 30s delay, the first time it becomes ready within a initialization period (300s) is the initial ready period.



Calculate desired replica's:
- Determine normally
- Determine inlcuding desiredReplica with not ready pods assuming 100% utilization for sclae-down and 0% for scale-up
- If scaling operation is reversed or is within tollerance: no scaling operation. Else scale to new ratio

When using multiple metrics, all desired replicas are chosen and scaling happens to the largest of them.

downscale-stabilization window. ALl recommendations are recordind. From all recommendations of the window, the highest is chosen.
(default: 300s)


Expose flink-jobmanager
```angular2html
kubectl expose pods flink-jobmanager-c4kwc --type=LoadBalancer --name=external-jobmanager
```
