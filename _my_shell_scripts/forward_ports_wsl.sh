#!/bin/bash

echo "Setting port forwards"
wt.exe new-tab ubuntu -c . ./my_shell_scripts/port_forwards_wsl/port_forward_flink.sh
wt.exe new-tab ubuntu -c . ./my_shell_scripts/port_forwards_wsl/port_forward_kafka.sh
wt.exe new-tab ubuntu -c . ./my_shell_scripts/port_forwards_wsl/port_forward_prometheus.sh
wt.exe new-tab ubuntu -c . ./my_shell_scripts/port_forwards_wsl/port_forward_grafana.sh
