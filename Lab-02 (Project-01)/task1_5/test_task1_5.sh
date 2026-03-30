#!/bin/sh
set -e

../../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

CLEAN_HDFS="/parking/clean"
REVENUE_HDFS="/parking/revenue_by_type"
REVENUE_FINAL_HDFS="/parking/revenue_by_type_final"

# Clean old outputs
$HDFS dfs -rm -r -f "$REVENUE_HDFS" || true
$HDFS dfs -rm -r -f "$REVENUE_FINAL_HDFS" || true


# Job 1: Map-side join + aggregate by violation type
$HADOOP jar "$STREAMING_JAR" \
  -files fine_lookup.csv,mapper_revenue.py,reducer_revenue.py \
  -mapper "python3 mapper_revenue.py" \
  -reducer "python3 reducer_revenue.py" \
  -input "$CLEAN_HDFS/*" \
  -output "$REVENUE_HDFS"


# Job 2: Revenue share + ranking
$HADOOP jar "$STREAMING_JAR" \
  -numReduceTasks 1 \
  -file ./mapper_share.py \
  -mapper "python3 mapper_share.py" \
  -file ./reducer_share.py \
  -reducer "python3 reducer_share.py" \
  -input "$REVENUE_HDFS/*" \
  -output "$REVENUE_FINAL_HDFS"

echo "=== Revenue by violation type ==="
$HDFS dfs -cat "$REVENUE_FINAL_HDFS/part-00000" || true

$HDFS dfs -cat "$REVENUE_FINAL_HDFS/part-00000" > task1_5_revenue_by_type.txt || true

../../../stop.sh
