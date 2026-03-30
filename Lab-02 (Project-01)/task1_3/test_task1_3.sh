#!/bin/sh
set -e

../../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

CLEAN_HDFS="/parking/clean"
HOTSPOT_HDFS="/parking/hotspots_top20"

$HDFS dfs -rm -r -f "$HOTSPOT_HDFS" || true

echo "=== Sample cleaned rows from HDFS ==="
$HDFS dfs -cat "$CLEAN_HDFS/part-*" | head -5 || true

$HADOOP jar "$STREAMING_JAR" \
  -numReduceTasks 1 \
  -file ./mapper_topk.py \
  -mapper "python3 mapper_topk.py" \
  -file ./reducer_topk.py \
  -reducer "python3 reducer_topk.py" \
  -input "$CLEAN_HDFS/*" \
  -output "$HOTSPOT_HDFS"

echo "=== Top 20 geographic hotspots ==="
$HDFS dfs -cat "$HOTSPOT_HDFS/part-*" || true

$HDFS dfs -cat "$HOTSPOT_HDFS/part-*" > task1_3_top20_hotspots.txt || true

../../../stop.sh
