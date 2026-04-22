# CISC 5950 - Lab 3: Spark Analytics Pipeline

## Authors
- Muhammad Zawad Mahmud (A23176102)
- Samiha Islam (A23171266)

## Overview
This lab re-implements four analytics tasks from Lab 2 (MapReduce) using Apache Spark, demonstrating how Spark's DataFrame API, broadcast joins, window functions, and MLlib replace complex MapReduce patterns with more concise and performant alternatives.

## Prerequisites
- 3-node HDFS cluster set up using [hdfs-test](https://github.com/yingmao/hdfs-test) and [mapreduce-test](https://github.com/yingmao/mapreduce-test)
- Apache Spark installed and configured (YARN mode), set up using [spark-examples](https://github.com/yingmao/spark-examples)
- Hadoop 3.4.2 with YARN

## Datasets
- **Part 1**: NYC Parking Violations CSV (~8.3M records) in HDFS at `/parking/raw/`
- **Part 2**: E-Commerce Clickstream CSV (~2M events) in HDFS at `/clickstream/raw/`

These are the same datasets used in Lab 2. If not already in HDFS, upload them:
```bash
hdfs dfs -mkdir -p /parking/raw
hdfs dfs -copyFromLocal parking_half.csv /parking/raw/

hdfs dfs -mkdir -p /clickstream/raw
hdfs dfs -copyFromLocal clickstream_large.csv /clickstream/raw/
```

## Folder Structure

```
spark-examples/
└── test-python/
    └── lab3/
        ├── Part1/
        │   ├── task1_1_cleaning.py
        │   ├── test_task1_1.sh
        │   ├── task1_2_hotspots.py
        │   └── test_task1_2.sh
        ├── Part2/
        │   ├── task2_1_sessions.py
        │   ├── test_task2_1.sh
        │   ├── task2_2_clustering.py
        │   └── test_task2_2.sh
        ├── README.md
        └── Report_Lab-03.pdf
```

## How to Run

Each task has a shell script that starts HDFS/YARN, runs the Spark job, and stops the cluster.

### Part 1: Urban Analytics with Spark

**Task 1.1 - Data Cleaning Pipeline Modernization**
```bash
cd spark-examples/test-python/lab3/Part1
bash test_task1_1.sh
```
Replaces the multi-job MapReduce cleaning pipeline with a single Spark job using DataFrame operations. Reads from `/parking/raw/`, writes cleaned data to `/parking/spark_clean/`. Must be run before Task 1.2.

**Task 1.2 - Geographic Hotspot Analysis with Broadcast Join**
```bash
cd spark-examples/test-python/lab3/Part1
bash test_task1_2.sh
```
Replaces MapReduce Top-K pattern and Map-Side Join with Spark's broadcast join and `groupBy().agg().orderBy().limit()`. Reads from `/parking/spark_clean/`, writes top 20 hotspots to `/parking/hotspots/`.

### Part 2: E-Commerce Analytics with Spark

**Task 2.1 - Session Reconstruction with Window Functions**
```bash
cd spark-examples/test-python/lab3/Part2
bash test_task2_1.sh
```
Replaces MapReduce Secondary Sort (custom partitioner/comparator) with Spark Window Functions using `lag()` for time gaps and cumulative sum for session IDs. Reads from `/clickstream/raw/`, writes sessions to `/clickstream/spark_sessions/`. Must be run before Task 2.2.

**Task 2.2 - Customer Segmentation with Spark MLlib**
```bash
cd spark-examples/test-python/lab3/Part2
bash test_task2_2.sh
```
Replaces iterative MapReduce K-Means (multiple jobs with HDFS I/O per iteration) with MLlib's optimized KMeans. Reads from `/clickstream/spark_sessions/`, writes cluster assignments to `/clickstream/spark_clusters/`.

## Execution Order

Tasks must be run in this order due to data dependencies:

1. **Task 1.1** (produces `/parking/spark_clean/` used by Task 1.2)
2. **Task 1.2** (reads from `/parking/spark_clean/`)
3. **Task 2.1** (produces `/clickstream/spark_sessions/` used by Task 2.2)
4. **Task 2.2** (reads from `/clickstream/spark_sessions/`)

## Output Locations

| Task | HDFS Output Path | Description |
|------|-----------------|-------------|
| 1.1 | `/parking/spark_clean/` | Cleaned parking violations CSV |
| 1.2 | `/parking/hotspots/` | Top 20 hotspots with revenue |
| 2.1 | `/clickstream/spark_sessions/` | Reconstructed user sessions |
| 2.2 | `/clickstream/spark_clusters/` | User cluster assignments with RFM features |

## Notes
- Part 1 uses approximately 8.3 million records (half of the full 16.5M dataset) due to cluster storage constraints.
- Part 2 uses approximately 2 million clickstream events.
