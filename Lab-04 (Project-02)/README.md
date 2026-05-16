# CISC 5950 - Lab 4: Spark ML/MLlib Project

## Authors
- Muhammad Zawad Mahmud (A23176102)
- Samiha Islam (A23171266)

## Overview
This lab applies Spark ML/MLlib to four machine learning tasks on a 3-node HDFS cluster: toxic comment text classification, heart disease prediction, census income classification using logistic regression, and a comparison of random forest and decision tree classifiers on census data.

## Prerequisites
- 3-node HDFS cluster set up using [hdfs-test](https://github.com/yingmao/hdfs-test) and [mapreduce-test](https://github.com/yingmao/mapreduce-test)
- Apache Spark installed and configured (YARN mode), set up using [spark-examples](https://github.com/yingmao/spark-examples)
- Hadoop 3.4.2 with YARN

## Setup

Copy the entire `lab4` folder into the `spark-examples/test-python/` directory on the cluster:

```bash
cp -r lab4 /spark-examples/test-python/
```

Then place the datasets in their respective folders as described below.

## Folder Structure

```
spark-examples/
└── test-python/
    └── lab4/
        ├── P1/
        │   ├── p1_text_classification.py
        │   ├── test_p1.sh
        │   ├── README.md
        │   ├── train.csv
        │   ├── test.csv
        │   └── test_labels.csv
        ├── P2/
        │   ├── p2_heart_disease.py
        │   ├── test_p2.sh
        │   ├── README.md
        │   └── framingham.csv
        ├── P3/
        │   ├── p3_census_lr.py
        │   ├── test_p3.sh
        │   ├── README.md
        │   ├── adult.data
        │   └── adult.test
        ├── P4/
        │   ├── p4_census_rf_dt.py
        │   ├── p3_census_lr.py  (copy from P3)
        │   ├── test_p4.sh
        │   ├── README.md
        │   ├── adult.data
        │   └── adult.test
        ├── README.md
        └── Report_lab4.pdf
```

## How to Run

Each part has its own README with detailed instructions. Follow them in order:

1. **P1** — Toxic Comment Classification → see `P1/README.md`
2. **P2** — Heart Disease Prediction → see `P2/README.md`
3. **P3** — Census Income (Logistic Regression) → see `P3/README.md`
4. **P4** — Census Income (Random Forest & Decision Tree) → see `P4/README.md`

All four parts are independent and can be run in any order. P4 requires `p3_census_lr.py` to be copied from the P3 folder. See P4's README for details.

