# CISC 5950 - Lab 4 (Option-1), P3: Census Income Classification (Logistic Regression)

## Authors
- Muhammad Zawad Mahmud (A23176102)
- Samiha Islam (A23171266)

## Overview
Logistic Regression on the UCI Adult Census Income dataset (~32K training, ~16K test) to predict whether income exceeds $50K/year. Features include 8 categorical and 6 numerical attributes processed through a StringIndexer + OneHotEncoder pipeline.

## Prerequisites
- 3-node HDFS cluster set up using [hdfs-test](https://github.com/yingmao/hdfs-test) and [mapreduce-test](https://github.com/yingmao/mapreduce-test)
- Apache Spark installed and configured (YARN mode), set up using [spark-examples](https://github.com/yingmao/spark-examples)
- Hadoop 3.4.2 with YARN

## Dataset
- `adult.data` — Training set (32,561 records, 14 attributes + income label)
- `adult.test` — Test set (16,281 records)

Both files from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/adult). Place them in the P3 folder before running.

## Folder Structure

```
spark-examples/
└── test-python/
    └── lab4/
        └── P3/
            ├── p3_census_lr.py
            ├── test_p3.sh
            ├── adult.data
            └── adult.test
```

## How to Run

```bash
cd spark-examples/test-python/lab4/P3
bash test_p3.sh
```
