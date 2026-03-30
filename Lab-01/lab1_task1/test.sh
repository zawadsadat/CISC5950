#!/bin/sh
set -e

../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

IN_HDFS="/lab1_task1/input"
OUT1_HDFS="/lab1_task1/output1"
OUT2_HDFS="/lab1_task1/output2"

# Clean
$HDFS dfs -rm -r -f "$IN_HDFS"  || true
$HDFS dfs -rm -r -f "$OUT1_HDFS" || true
$HDFS dfs -rm -r -f "$OUT2_HDFS" || true

# Input (CHANGE THIS to your real log file)
$HDFS dfs -mkdir -p "$IN_HDFS"
$HDFS dfs -copyFromLocal ../../mapreduce-test-data/access-1m.log.txt "$IN_HDFS"

# Stage 1
$HADOOP jar "$STREAMING_JAR" \
  -file ./mapper-1.py \
  -mapper "python3 mapper-1.py" \
  -file ./reducer-1.py \
  -reducer "python3 reducer-1.py" \
  -input "$IN_HDFS/*" \
  -output "$OUT1_HDFS"

# Stage 2
$HADOOP jar "$STREAMING_JAR" \
  -file ./mapper-2.py \
  -mapper "python3 mapper-2.py" \
  -file ./reducer-2.py \
  -reducer "python3 reducer-2.py" \
  -input "$OUT1_HDFS/*" \
  -output "$OUT2_HDFS"

# Show results (example: last 50 lines)
$HDFS dfs -cat "$OUT2_HDFS/part-00000" | tail -50
$HDFS dfs -cat "$OUT2_HDFS/part-00000" > task1_output.txt

../../stop.sh
