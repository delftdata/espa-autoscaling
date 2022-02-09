#!/bin/bash

until python ds2Logic.py
do
    echo "Restarting"
    sleep 2
done