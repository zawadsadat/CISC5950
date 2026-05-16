# CISC 5950 - Lab 4 (Option-1), P2: Heart Disease Prediction

## Authors
- Muhammad Zawad Mahmud (A23176102)
- Samiha Islam (A23171266)

## Overview
Logistic Regression on the Framingham Heart Study dataset (~4,240 records) to predict 10-year coronary heart disease risk. The sample Python code from the lab specification is converted to a Spark ML pipeline.

## Prerequisites
- 3-node HDFS cluster set up using [hdfs-test](https://github.com/yingmao/hdfs-test) and [mapreduce-test](https://github.com/yingmao/mapreduce-test)
- Apache Spark installed and configured (YARN mode), set up using [spark-examples](https://github.com/yingmao/spark-examples)
- Hadoop 3.4.2 with YARN

## Dataset
- `framingham.csv` — 4,240 patient records with 16 columns (age, sex, cigsPerDay, totChol, sysBP, diaBP, BMI, heartRate, glucose, TenYearCHD, etc.)

Place the file in the P2 folder before running.

## Folder Structure

```
spark-examples/
└── test-python/
    └── lab4/
        └── P2/
            ├── p2_heart_disease.py
            ├── test_p2.sh
            └── framingham.csv
```

## How to Run

```bash
cd spark-examples/test-python/lab4/P2
bash test_p2.sh
```
