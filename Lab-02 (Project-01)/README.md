# CISC 5950 - Lab 2: MapReduce Analytics Pipeline

## Prerequisites
- 3-node HDFS cluster set up using [hdfs-test](https://github.com/yingmao/hdfs-test) and [mapreduce-test](https://github.com/yingmao/mapreduce-test)
- Hadoop 3.4.2 with YARN
- Python 3

## Datasets
- **Part 1**: Place the parking violations CSV (data/Part 1/parking_half.csv) in `mapreduce-test-data/parking_half.csv`
- **Part 2**: Place the clickstream CSV (data/Part 2/clickstream_large.csv) in `mapreduce-test-data/clickstream_large.csv`

## Folder Structure

mapreduce-test/
├── mapreduce-test-data/
│   ├── parking_half.csv
│   └── clickstream_large.csv
└── mapreduce-test-python/
    └── lab2/
        ├── task1_1/
        │   ├── mapper_clean.py
        │   ├── reducer_clean.py
        │   ├── mapper_quality.py
        │   ├── reducer_quality.py
        │   └── test_task1_1.sh
        ├── task1_2/
        │   ├── mapper_hourly.py
        │   ├── reducer_hourly.py
        │   ├── mapper_window.py
        │   ├── reducer_window.py
        │   └── test_task1_2.sh
        ├── task1_3/
        │   ├── mapper_topk.py
        │   ├── reducer_topk.py
        │   └── test_task1_3.sh
        ├── task1_4/
        │   ├── mapper_profile.py
        │   ├── reducer_profile.py
        │   ├── mapper_risk.py
        │   ├── reducer_risk.py
        │   └── test_task1_4.sh
        ├── task1_5/
        │   ├── mapper_revenue.py
        │   ├── reducer_revenue.py
        │   ├── mapper_share.py
        │   ├── reducer_share.py
        │   ├── fine_lookup.csv
        │   └── test_task1_5.sh
        ├── task2_1/
        │   ├── mapper_session.py
        │   ├── reducer_session.py
        │   └── test_task2_1.sh
        └── task2_2/
            ├── mapper_features.py
            ├── reducer_features.py
            ├── mapper_kmeans.py
            ├── combiner_kmeans.py
            ├── reducer_kmeans.py
            ├── mapper_assign_clusters.py
            ├── reducer_cluster_summary.py
            ├── centroids.txt
            └── test_task2_2.sh

## How to Run

Each task has its own shell script that starts the cluster, uploads data to HDFS, runs the MapReduce job(s), and saves the output locally.

### Part 1: Urban Analytics Pipeline

**Task 1.1 - Data Cleaning & Quality Report**
```
cd mapreduce-test-python/lab2/task1_1
bash test_task1_1.sh
```
This must be run first as all subsequent Part 1 tasks read from `/parking/clean` in HDFS.

**Task 1.2 - Peak Enforcement Time Analysis**
```
cd mapreduce-test-python/lab2/task1_2
bash test_task1_2.sh
```

**Task 1.3 - Geographic Hotspot Identification**
```
cd mapreduce-test-python/lab2/task1_3
bash test_task1_3.sh
```

**Task 1.4 - Vehicle Risk Profiling**
```
cd mapreduce-test-python/lab2/task1_4
bash test_task1_4.sh
```

**Task 1.5 - Revenue Analysis by Violation Type**
```
cd mapreduce-test-python/lab2/task1_5
bash test_task1_5.sh
```

### Part 2: E-Commerce Analytics

**Task 2.1 - User Session Reconstruction**
```
cd mapreduce-test-python/lab2/task2_1
bash test_task2_1.sh
```
This must be run before Task 2.2 as it produces the session data in `/clickstream/sessions`.

**Task 2.2 - K-Means Customer Segmentation**
```
cd mapreduce-test-python/lab2/task2_2
bash test_task2_2.sh
```
Make sure `centroids.txt` contains the initial centroids before running:
```
0,0.10,0.60,0.70
1,0.25,0.30,0.30
2,0.70,0.40,0.40
3,0.15,0.08,0.05
```

## Execution Order

Tasks must be run in this order due to data dependencies:

1. **Task 1.1** (produces `/parking/clean` used by Tasks 1.2-1.5)
2. Tasks 1.2, 1.3, 1.4, 1.5 (can be run in any order after 1.1)
3. **Task 2.1** (produces `/clickstream/sessions` used by Task 2.2)
4. **Task 2.2** (reads from `/clickstream/sessions` and `/clickstream/user_features`)

## Output Files

Each task saves its output locally in the task folder:

| Task | Output File(s) |
|------|---------------|
| 1.1 | `task1_1_clean_sample.csv`, `task1_1_quality_report.csv` |
| 1.2 | `task1_2_hourly_counts.txt`, `task1_2_peak_window.txt` |
| 1.3 | `task1_3_top20_hotspots.txt` |
| 1.4 | `task1_4_vehicle_profiles.txt`, `task1_4_vehicle_risk.txt` |
| 1.5 | `task1_5_revenue_by_type.txt` |
| 2.1 | `task2_1_sessions.csv` |
| 2.2 | `task2_2_user_features.csv`, `task2_2_final_centroids.txt`, `task2_2_cluster_summary.txt` |

