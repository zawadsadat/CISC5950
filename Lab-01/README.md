# CISC 5950 - Lab 1: Detecting Suspicious Users in Web Logs with MapReduce Streaming

## Prerequisites
- 3-node HDFS cluster set up using [hdfs-test](https://github.com/yingmao/hdfs-test) and [mapreduce-test](https://github.com/yingmao/mapreduce-test)
- Hadoop 3.4.2 with YARN
- Python 3

## Dataset
- Place the web log file (data/access-1m.log.txt) in `mapreduce-test-data/access-1m.log.txt`

## Folder Structure

mapreduce-test/
├── mapreduce-test-data/
│   └── access-1m.log.txt
└── mapreduce-test-python/
    ├── lab1_task1/
    │   ├── mapper-1.py
    │   ├── reducer-1.py
    │   ├── mapper-2.py
    │   ├── reducer-2.py
    │   └── test.sh
    └── lab1_task2/
        ├── mapper-1.py
        ├── reducer-1.py
        ├── mapper-2.py
        ├── reducer-2.py
        └── test.sh

## How to Run

Each task has its own shell script that starts the cluster, uploads data to HDFS, runs the MapReduce job(s), and saves the output locally.

**Task 1**
```
cd mapreduce-test-python/lab1_task1
bash test.sh
```

**Task 2**
```
cd mapreduce-test-python/lab1_task2
bash test.sh
```

## Execution Order

Tasks should be run in order:

1. **Task 1** (run first)
2. **Task 2** (run after Task 1)

## Output Files

| Task | Output File |
|------|------------|
| 1 | `task1_output.txt` |
| 2 | `task2_output.txt` |
