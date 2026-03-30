#!/bin/sh
set -e

../../../start.sh

HDFS="/usr/local/hadoop/bin/hdfs"
HADOOP="/usr/local/hadoop/bin/hadoop"
STREAMING_JAR="/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.2.jar"

SESSION_HDFS="/clickstream/sessions"
FEATURE_HDFS="/clickstream/user_features"
SUMMARY_HDFS="/clickstream/cluster_summary"

MAX_ITER=15
EPS=0.001

# Clean old outputs
$HDFS dfs -rm -r -f "$FEATURE_HDFS" || true
$HDFS dfs -rm -r -f "$SUMMARY_HDFS" || true
for i in $(seq 1 $MAX_ITER)
do
  $HDFS dfs -rm -r -f "/clickstream/kmeans_iter_$i" || true
done


# Job 1: Build user RFM features
$HADOOP jar "$STREAMING_JAR" \
  -file ./mapper_features.py \
  -mapper "python3 mapper_features.py" \
  -file ./reducer_features.py \
  -reducer "python3 reducer_features.py" \
  -input "$SESSION_HDFS/*" \
  -output "$FEATURE_HDFS"


# Iterative K-means with convergence check
ITER=1
CONVERGED=0

while [ $ITER -le $MAX_ITER ] && [ $CONVERGED -eq 0 ]
do
  OUT="/clickstream/kmeans_iter_$ITER"

  cp centroids.txt centroids_prev.txt

  $HADOOP jar "$STREAMING_JAR" \
    -numReduceTasks 1 \
    -file ./centroids.txt \
    -file ./mapper_kmeans.py \
    -file ./combiner_kmeans.py \
    -file ./reducer_kmeans.py \
    -mapper "python3 mapper_kmeans.py" \
    -combiner "python3 combiner_kmeans.py" \
    -reducer "python3 reducer_kmeans.py" \
    -input "$FEATURE_HDFS/*" \
    -output "$OUT"

  $HDFS dfs -cat "$OUT/part-*" > centroids.txt

  # convergence check
  set +e
  python3 - <<PY
import csv, math, sys

eps = float("$EPS")

def load(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 4:
                rows.append((row[0].strip(), [float(x) for x in row[1:4]]))
    rows.sort(key=lambda x: x[0])
    return rows

old = load("centroids_prev.txt")
new = load("centroids.txt")

if len(old) != len(new):
    print("Centroid count mismatch")
    sys.exit(2)

maxdiff = 0.0
for (cid1, v1), (cid2, v2) in zip(old, new):
    if cid1 != cid2:
        print("Centroid ID mismatch")
        sys.exit(2)
    diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
    if diff > maxdiff:
        maxdiff = diff

print(f"Max centroid movement: {maxdiff:.6f}")

if maxdiff < eps:
    sys.exit(0)   # converged
else:
    sys.exit(1)   # not converged yet
PY
  STATUS=$?
  set -e

  if [ $STATUS -eq 0 ]; then
    CONVERGED=1
    echo "Converged at iteration $ITER"
  elif [ $STATUS -eq 1 ]; then
    echo "Not converged after iteration $ITER, continuing..."
  else
    echo "Convergence check failed"
    exit 1
  fi

  ITER=$((ITER + 1))
done


# Final cluster summary
$HADOOP jar "$STREAMING_JAR" \
  -numReduceTasks 1 \
  -file ./centroids.txt \
  -file ./mapper_assign_clusters.py \
  -mapper "python3 mapper_assign_clusters.py" \
  -file ./reducer_cluster_summary.py \
  -reducer "python3 reducer_cluster_summary.py" \
  -input "$FEATURE_HDFS/*" \
  -output "$SUMMARY_HDFS"

# Save outputs locally with headers
echo "user_id,R,F,M" > task2_2_user_features.csv
$HDFS dfs -cat "$FEATURE_HDFS/part-*" >> task2_2_user_features.csv || true

cp centroids.txt task2_2_final_centroids.txt
$HDFS dfs -cat "$SUMMARY_HDFS/part-*" > task2_2_cluster_summary.txt || true

echo "=== User Features (RFM) ==="
head -20 task2_2_user_features.csv || true

echo "=== Final Centroids ==="
cat task2_2_final_centroids.txt || true

echo "=== Cluster Summary ==="
cat task2_2_cluster_summary.txt || true

../../../stop.sh
