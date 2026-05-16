# CISC 5950 — Big Data Computing
**Fordham University · Spring 2026**

Labs and projects covering the full big-data stack: Hadoop, MapReduce, and Apache Spark — applied to real-world datasets in urban analytics, e-commerce, and machine learning.

---

## Course Progression

| # | Folder | Topic | Key Technologies |
|---|--------|-------|-----------------|
| 1 | `Lab-01` | Suspicious User Detection in Web Logs | Hadoop Streaming, MapReduce (2-stage), HDFS |
| 2 | `Lab-02 (Project-01)` | Advanced MapReduce Analytics Pipeline | MapReduce Patterns (Top-K, Secondary Sort, Map-Side Join, Custom Writable, Iterative MR), YARN |
| 3 | `Lab-03` | Spark Analytics Pipeline | Apache Spark, DataFrame API, Broadcast Joins, Window Functions, Spark MLlib (K-Means) |
| 4 | `Lab-04 (Project-02)` | Spark ML Classification Suite | PySpark ML/MLlib, Logistic Regression, Random Forest, Decision Tree, 3-node Spark Cluster |

---

## Skills Demonstrated

- 3-node Hadoop/Spark cluster setup and job submission
- MapReduce design patterns: Top-K, Secondary Sort, Map-Side Join, Custom Writable, Iterative MapReduce
- Spark DataFrame API, lazy evaluation, DAG optimization, in-memory caching
- Spark MLlib: classification (Logistic Regression, Random Forest, Decision Tree) and clustering (K-Means)
- RFM feature engineering and customer segmentation
- Text mining and NLP preprocessing with `pyspark.ml`
- Performance benchmarking: MapReduce vs. Spark

---

## Environment

- **Cluster:** 3-node (1 master + 2 workers), Hadoop + Spark standalone / YARN
- **Language:** Python 3 (PySpark)
- **Storage:** HDFS

---

## Repository Structure

```
CISC5950/
├── Lab-01/                  # Hadoop Streaming — Suspicious User Detection
├── Lab-02 (Project-01)/     # Advanced MapReduce Analytics Pipeline
├── Lab-03/                  # Spark Analytics Pipeline (MapReduce → Spark migration)
└── Lab-04 (Project-02)/     # Spark ML Classification Suite
    ├── P1/                  # Toxic Comment Classification
    ├── P2/                  # Heart Disease Prediction
    ├── P3/                  # Census Income Classification
    ├── P4/                  # Random Forest & Decision Tree on Census Data
    ├── report.pdf
    └── README.md
```
