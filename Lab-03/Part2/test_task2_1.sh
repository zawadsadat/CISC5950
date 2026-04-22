#!/bin/bash
# Task 2.1: Session Reconstruction with Window Functions
# Run from /spark-examples/test-python/lab3/Part2/

cd ../../../../mapreduce-test && bash start.sh
cd /spark-examples/test-python/lab3/Part2

/usr/local/spark/bin/spark-submit \
  --master yarn \
  --conf spark.ui.enabled=false \
  --num-executors 3 \
  --executor-memory 1g \
  --driver-memory 1g \
  task2_1_sessions.py

cd ../../../../mapreduce-test && bash stop.sh
