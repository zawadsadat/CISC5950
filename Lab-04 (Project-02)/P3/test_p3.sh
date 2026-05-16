#!/bin/bash
# Lab 4 Part 3: Census Income - Logistic Regression
# Run from /spark-examples/test-python/lab4/P3/

cd ../../../../../mapreduce-test && bash start.sh
cd /spark-examples/test-python/lab4/P3

# Upload data to HDFS if not already there
hdfs dfs -mkdir -p /lab4/data
hdfs dfs -test -e /lab4/data/adult.data
if [ $? -ne 0 ]; then
    echo "Uploading adult.data to HDFS..."
    hdfs dfs -copyFromLocal adult.data /lab4/data/
fi
hdfs dfs -test -e /lab4/data/adult.test
if [ $? -ne 0 ]; then
    echo "Uploading adult.test to HDFS..."
    hdfs dfs -copyFromLocal adult.test /lab4/data/
fi

/usr/local/spark/bin/spark-submit \
  --master yarn \
  --conf spark.ui.enabled=false \
  --num-executors 3 \
  --executor-memory 1g \
  --driver-memory 1g \
  p3_census_lr.py

cd ../../../../../mapreduce-test && bash stop.sh
