#!/bin/bash
# Task 1.2: Geographic Hotspot Analysis with Broadcast Join
# Run from /spark-examples/test-python/lab3/Part1/

cd ../../../../mapreduce-test && bash start.sh
cd /spark-examples/test-python/lab3/Part1

/usr/local/spark/bin/spark-submit \
  --master yarn \
  --conf spark.ui.enabled=false \
  --num-executors 3 \
  --executor-memory 1g \
  --driver-memory 1g \
  task1_2_hotspots.py

cd ../../../../mapreduce-test && bash stop.sh
