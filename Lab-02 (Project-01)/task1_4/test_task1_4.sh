#!/bin/sh
set -e

../../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

CLEAN_HDFS="/parking/clean"
PROFILE_HDFS="/parking/vehicle_profiles"
RISK_HDFS="/parking/vehicle_risk"

# Clean old outputs
$HDFS dfs -rm -r -f "$PROFILE_HDFS" || true
$HDFS dfs -rm -r -f "$RISK_HDFS" || true


# Job 1: Build vehicle profiles
$HADOOP jar "$STREAMING_JAR" \
  -file ./mapper_profile.py \
  -mapper "python3 mapper_profile.py" \
  -file ./reducer_profile.py \
  -reducer "python3 reducer_profile.py" \
  -input "$CLEAN_HDFS/*" \
  -output "$PROFILE_HDFS"


# Job 2: Vehicle risk analytics
$HADOOP jar "$STREAMING_JAR" \
  -numReduceTasks 1 \
  -file ./mapper_risk.py \
  -mapper "python3 mapper_risk.py" \
  -file ./reducer_risk.py \
  -reducer "python3 reducer_risk.py" \
  -input "$PROFILE_HDFS/*" \
  -output "$RISK_HDFS"

echo "=== Sample vehicle profiles ==="
$HDFS dfs -cat "$PROFILE_HDFS/part-*" | head -10 || true

echo "=== Vehicle risk profiling output ==="
$HDFS dfs -cat "$RISK_HDFS/part-*" || true

# Save locally with header for profiles
echo -e "Vehicle_Key\tDominant_Color\tTicket_Count" > task1_4_vehicle_profiles.txt
$HDFS dfs -cat "$PROFILE_HDFS/part-*" | head -20 >> task1_4_vehicle_profiles.txt || true

$HDFS dfs -cat "$RISK_HDFS/part-*" > task1_4_vehicle_risk.txt || true

../../../stop.sh
