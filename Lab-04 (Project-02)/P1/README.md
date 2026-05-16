# CISC 5950 - Lab 4 (Option-1), P1: Toxic Comment Classification

## Authors
- Muhammad Zawad Mahmud (A23176102)
- Samiha Islam (A23171266)

## Overview
Text classification using Spark MLlib to identify toxic comments from the Jigsaw Toxic Comment Classification dataset (~560K comments). A binary label is created (toxic if any of the six toxicity categories is flagged) and classified using a TF-IDF + Logistic Regression pipeline.

## Prerequisites
- 3-node HDFS cluster set up using [hdfs-test](https://github.com/yingmao/hdfs-test) and [mapreduce-test](https://github.com/yingmao/mapreduce-test)
- Apache Spark installed and configured (YARN mode), set up using [spark-examples](https://github.com/yingmao/spark-examples)
- Hadoop 3.4.2 with YARN

## Dataset
- `train.csv` — ~560K labeled comments (6 toxicity categories)
- `test.csv` — Test comments
- `test_labels.csv` — Test labels (-1 indicates unlabeled, filtered out)

Place all three files in the P1 folder before running.

## Folder Structure

```
spark-examples/
└── test-python/
    └── lab4/
        └── P1/
            ├── p1_text_classification.py
            ├── test_p1.sh
            ├── train.csv
            ├── test.csv
            └── test_labels.csv
```

## How to Run

```bash
cd spark-examples/test-python/lab4/P1
bash test_p1.sh
```

