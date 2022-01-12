#!/bin/bash

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_flink.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_kafka.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_prometheus.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_grafana.sh