#!/bin/bash

wt.exe new-tab ubuntu -c . port_forward_flink.sh

wt.exe new-tab ubuntu -c . port_forward_kafka.sh

wt.exe new-tab ubuntu -c . port_forward_prometheus.sh

wt.exe new-tab ubuntu -c . port_forward_grafana.sh