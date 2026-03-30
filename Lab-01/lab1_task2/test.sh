#!/bin/sh
set -e

../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

RANGE="$1"  # example: 00-06
if [ -z "$RANGE" ]; then
  echo "Usage: bash test.sh 00-06"
  echo "Example: bash test.sh 22-02"
  exit 1
fi

IN_HDFS="/lab1_task1/input"
OUT1_HDFS="/lab1/task2_output1"
OUT2_HDFS="/lab1/task2_output2"

# Clean
$HDFS dfs -rm -r -f "$IN_HDFS" || true
$HDFS dfs -rm -r -f "$OUT1_HDFS" || true
$HDFS dfs -rm -r -f "$OUT2_HDFS" || true

# If you already uploaded input for Task-01, keep it.
# Otherwise uncomment these 2 lines to load input:
$HDFS dfs -mkdir -p "$IN_HDFS"
$HDFS dfs -copyFromLocal ../../mapreduce-test-data/access-500k.log.txt "$IN_HDFS"

# Stage 1 (filter by range + compute scores per hour/ip)
$HADOOP jar "$STREAMING_JAR" \
  -file ./mapper-1.py \
  -mapper "python3 mapper-1.py $RANGE" \
  -file ./reducer-1.py \
  -reducer "python3 reducer-1.py" \
  -input "$IN_HDFS/*" \
  -output "$OUT1_HDFS"

# Stage 2 (global top-3 across the range)
$HADOOP jar "$STREAMING_JAR" \
  -numReduceTasks 1 \
  -file ./mapper-2.py \
  -mapper "python3 mapper-2.py" \
  -file ./reducer-2.py \
  -reducer "python3 reducer-2.py" \
  -input "$OUT1_HDFS/*" \
  -output "$OUT2_HDFS"

# Print and save output for report screenshots
$HDFS dfs -cat "$OUT2_HDFS/part-00000"
$HDFS dfs -cat "$OUT2_HDFS/part-00000" > task2_output.txt

../../stop.sh
