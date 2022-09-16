#!/bin/bash

until python dhalionLogic.py
do
    echo "Restarting"
    sleep 2
done