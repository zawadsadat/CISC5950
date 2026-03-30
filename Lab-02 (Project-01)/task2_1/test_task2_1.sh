#!/bin/sh
set -e

../../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

LOCAL_INPUT="../../../mapreduce-test-data/clickstream_large.csv"

RAW_HDFS="/clickstream/raw"
SESSION_HDFS="/clickstream/sessions"

$HDFS dfs -rm -r -f "$RAW_HDFS" || true
$HDFS dfs -rm -r -f "$SESSION_HDFS" || true

$HDFS dfs -mkdir -p "$RAW_HDFS"
$HDFS dfs -copyFromLocal "$LOCAL_INPUT" "$RAW_HDFS"

$HADOOP jar "$STREAMING_JAR" \
  -D stream.num.map.output.key.fields=2 \
  -D mapreduce.job.reduces=2 \
  -D mapreduce.partition.keypartitioner.options=-k1,1 \
  -D mapreduce.partition.keycomparator.options='-k1,1 -k2,2' \
  -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner \
  -file ./mapper_session.py \
  -mapper "python3 mapper_session.py" \
  -file ./reducer_session.py \
  -reducer "python3 reducer_session.py" \
  -input "$RAW_HDFS/*" \
  -output "$SESSION_HDFS"

echo "=== Sample reconstructed sessions ==="
$HDFS dfs -cat "$SESSION_HDFS/part-*" | head -20 || true

$HDFS dfs -cat "$SESSION_HDFS/part-*" > task2_1_sessions.csv || true

../../../stop.sh
