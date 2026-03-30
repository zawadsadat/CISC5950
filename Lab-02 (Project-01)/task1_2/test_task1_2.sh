#!/bin/sh
set -e

../../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

CLEAN_HDFS="/parking/clean"
HOURLY_HDFS="/parking/hourly_counts"
WINDOW_HDFS="/parking/peak_window"

# Clean old outputs
$HDFS dfs -rm -r -f "$HOURLY_HDFS" || true
$HDFS dfs -rm -r -f "$WINDOW_HDFS" || true


# Job 1: Hourly counts
$HADOOP jar "$STREAMING_JAR" \
  -file ./mapper_hourly.py \
  -mapper "python3 mapper_hourly.py" \
  -file ./reducer_hourly.py \
  -reducer "python3 reducer_hourly.py" \
  -input "$CLEAN_HDFS/*" \
  -output "$HOURLY_HDFS"


# Job 2: Best 4-hour window
$HADOOP jar "$STREAMING_JAR" \
  -numReduceTasks 1 \
  -file ./mapper_window.py \
  -mapper "python3 mapper_window.py" \
  -file ./reducer_window.py \
  -reducer "python3 reducer_window.py" \
  -input "$HOURLY_HDFS/*" \
  -output "$WINDOW_HDFS"

echo "=== Hourly ticket counts ==="
$HDFS dfs -cat "$HOURLY_HDFS/part-*" | sort -n || true

echo "=== Best 4-hour enforcement window ==="
$HDFS dfs -cat "$WINDOW_HDFS/part-*" || true

# Save outputs locally with headers
echo -e "Hour\tTickets" > task1_2_hourly_counts.txt
$HDFS dfs -cat "$HOURLY_HDFS/part-*" | sort -n >> task1_2_hourly_counts.txt || true

$HDFS dfs -cat "$WINDOW_HDFS/part-*" > task1_2_peak_window.txt || true

../../../stop.sh
