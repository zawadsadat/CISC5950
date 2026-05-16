# CISC 5950 - Lab 4 (Option-1), P4: Census Income (Random Forest & Decision Tree)

## Authors
- Muhammad Zawad Mahmud (A23176102)
- Samiha Islam (A23171266)

## Overview
Redo P3 using Random Forest Classifier (100 trees, max depth 10) and Decision Tree Classifier (max depth 10) on the same UCI Adult Census Income dataset. Uses the same feature engineering pipeline from P3 and compares all three classifiers.

## Prerequisites
- 3-node HDFS cluster set up using [hdfs-test](https://github.com/yingmao/hdfs-test) and [mapreduce-test](https://github.com/yingmao/mapreduce-test)
- Apache Spark installed and configured (YARN mode), set up using [spark-examples](https://github.com/yingmao/spark-examples)
- Hadoop 3.4.2 with YARN

## Dataset
- `adult.data` — Training set (32,561 records)
- `adult.test` — Test set (16,281 records)

Same files as P3. Place them in the P4 folder before running.

## Folder Structure

```
spark-examples/
└── test-python/
    └── lab4/
        └── P4/
            ├── p4_census_rf_dt.py
            ├── p3_census_lr.py  (copy from P3)
            ├── test_p4.sh
            ├── adult.data
            └── adult.test
```

## How to Run

```bash
# Copy shared functions from P3 first
cp spark-examples/test-python/lab4/P3/p3_census_lr.py spark-examples/test-python/lab4/P4/

cd spark-examples/test-python/lab4/P4
bash test_p4.sh
```
