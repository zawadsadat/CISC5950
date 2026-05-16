#!/bin/bash
# Lab 4 Part 1: Text Classification with Spark MLlib
# Run from /spark-examples/test-python/lab4/P1/

cd ../../../../../mapreduce-test && bash start.sh
cd /spark-examples/test-python/lab4/P1

# Upload data to HDFS if not already there
hdfs dfs -mkdir -p /lab4/data
hdfs dfs -test -e /lab4/data/train.csv
if [ $? -ne 0 ]; then
    echo "Uploading training data to HDFS..."
    hdfs dfs -copyFromLocal train.csv /lab4/data/
fi
hdfs dfs -test -e /lab4/data/test.csv
if [ $? -ne 0 ]; then
    echo "Uploading test data to HDFS..."
    hdfs dfs -copyFromLocal test.csv /lab4/data/
fi
hdfs dfs -test -e /lab4/data/test_labels.csv
if [ $? -ne 0 ]; then
    echo "Uploading test labels to HDFS..."
    hdfs dfs -copyFromLocal test_labels.csv /lab4/data/
fi

/usr/local/spark/bin/spark-submit \
  --master yarn \
  --conf spark.ui.enabled=false \
  --num-executors 3 \
  --executor-memory 1g \
  --driver-memory 1g \
  p1_text_classification.py

cd ../../../../../mapreduce-test && bash stop.sh
