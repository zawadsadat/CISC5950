#!/bin/bash
# Task 1.1: Data Cleaning Pipeline
# Run from /spark-examples/test-python/lab3/Part1/

cd ../../../../mapreduce-test && bash start.sh
cd /spark-examples/test-python/lab3/Part1

/usr/local/spark/bin/spark-submit \
  --master yarn \
  --conf spark.ui.enabled=false \
  --num-executors 3 \
  --executor-memory 1g \
  --driver-memory 1g \
  task1_1_cleaning.py

cd ../../../../mapreduce-test && bash stop.sh
