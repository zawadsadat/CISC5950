#!/bin/sh
set -e

../../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

LOCAL_INPUT="../../../mapreduce-test-data/parking_half.csv"

RAW_HDFS="/parking/raw"
CLEAN_HDFS="/parking/clean"
QUALITY_HDFS="/parking/quality_report"

# Clean old outputs
$HDFS dfs -rm -r -f "$RAW_HDFS" || true
$HDFS dfs -rm -r -f "$CLEAN_HDFS" || true
$HDFS dfs -rm -r -f "$QUALITY_HDFS" || true

# Upload raw input
$HDFS dfs -mkdir -p "$RAW_HDFS"
$HDFS dfs -copyFromLocal "$LOCAL_INPUT" "$RAW_HDFS"


# Job 1: Clean dataset
$HADOOP jar "$STREAMING_JAR" \
  -file ./mapper_clean.py \
  -mapper "python3 mapper_clean.py" \
  -file ./reducer_clean.py \
  -reducer "python3 reducer_clean.py" \
  -input "$RAW_HDFS/*" \
  -output "$CLEAN_HDFS"


# Job 2: Quality report
$HADOOP jar "$STREAMING_JAR" \
  -file ./mapper_quality.py \
  -mapper "python3 mapper_quality.py" \
  -file ./reducer_quality.py \
  -reducer "python3 reducer_quality.py" \
  -input "$RAW_HDFS/*" \
  -output "$QUALITY_HDFS"

echo "=== Sample cleaned rows ==="
$HDFS dfs -cat "$CLEAN_HDFS/part-00000" | head -10 || true

echo "=== Quality report ==="
$HDFS dfs -cat "$QUALITY_HDFS/part-00000" || true

$HDFS dfs -cat "$CLEAN_HDFS/part-00000" | head -20 > task1_1_clean_sample.csv || true
$HDFS dfs -cat "$QUALITY_HDFS/part-00000" > task1_1_quality_report.csv || true

../../../stop.sh
