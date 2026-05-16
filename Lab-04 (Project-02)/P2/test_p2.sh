#!/bin/bash
# Lab 4 Part 2: Heart Disease Prediction
# Run from /spark-examples/test-python/lab4/P2/

cd ../../../../../mapreduce-test && bash start.sh
cd /spark-examples/test-python/lab4/P2

# Upload data to HDFS if not already there
hdfs dfs -mkdir -p /lab4/data
hdfs dfs -test -e /lab4/data/framingham.csv
if [ $? -ne 0 ]; then
    echo "Uploading Framingham dataset to HDFS..."
    hdfs dfs -copyFromLocal framingham.csv /lab4/data/
fi

/usr/local/spark/bin/spark-submit \
  --master yarn \
  --conf spark.ui.enabled=false \
  --num-executors 3 \
  --executor-memory 1g \
  --driver-memory 1g \
  p2_heart_disease.py

cd ../../../../../mapreduce-test && bash stop.sh
