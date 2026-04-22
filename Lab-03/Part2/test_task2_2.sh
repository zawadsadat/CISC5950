#!/bin/bash
# Task 2.2: Customer Segmentation with Spark MLlib K-Means
# Run from /spark-examples/test-python/lab3/Part2/

cd ../../../../mapreduce-test && bash start.sh
cd /spark-examples/test-python/lab3/Part2

/usr/local/spark/bin/spark-submit \
  --master yarn \
  --conf spark.ui.enabled=false \
  --num-executors 3 \
  --executor-memory 1g \
  --driver-memory 1g \
  task2_2_clustering.py

cd ../../../../mapreduce-test && bash stop.sh
