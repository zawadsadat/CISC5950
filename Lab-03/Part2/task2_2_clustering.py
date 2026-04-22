from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, lit, datediff, countDistinct, trim,
    sum as spark_sum, max as spark_max, count as spark_count
)
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler


def main():
    spark = SparkSession.builder \
        .appName("Lab3_Task2_2_KMeans") \
        .getOrCreate()

    # Read session data from Task 2.1
    sessions_df = spark.read.csv(
        "/clickstream/spark_sessions/",
        header=True,
        inferSchema=True
    )

    # Calculate RFM features
    # Get the latest date in the dataset as reference
    latest_date = sessions_df.agg(spark_max("end_time")).collect()[0][0]
    print(f"\nReference date (latest activity): {latest_date}")

    # Aggregate per user
    user_rfm = sessions_df \
        .groupBy("user_id") \
        .agg(
            # R: days since last activity / 90, capped at 1.0
            (datediff(lit(latest_date), spark_max("end_time")) / 90.0)
                .alias("recency_raw"),
            # F: distinct sessions / 50, capped at 1.0
            (spark_count("*") / 50.0).alias("frequency_raw"),
            # M: total purchase value / 5000, capped at 1.0
            (spark_sum(
                when(col("converted") == True, col("total_revenue")).otherwise(0.0)
            ) / 5000.0).alias("monetary_raw"),
        ) \
        .withColumn("recency",
            when(col("recency_raw") > 1.0, 1.0).otherwise(col("recency_raw"))) \
        .withColumn("frequency",
            when(col("frequency_raw") > 1.0, 1.0).otherwise(col("frequency_raw"))) \
        .withColumn("monetary",
            when(col("monetary_raw") > 1.0, 1.0).otherwise(col("monetary_raw")))

    # Assemble feature vector
    assembler = VectorAssembler(
        inputCols=["recency", "frequency", "monetary"],
        outputCol="features"
    )
    features_df = assembler.transform(user_rfm).cache()

    total_users = features_df.count()
    print(f"Total users for clustering: {total_users:,}")

    # Run K-Means 
    kmeans = KMeans(k=4, seed=42, maxIter=15, tol=0.001)
    model = kmeans.fit(features_df)
    predictions = model.transform(features_df)

    # Convergence Report
    print("\n" + "=" * 60)
    print("CONVERGENCE REPORT")
    print("=" * 60)
    summary = model.summary
    print(f"Iterations to convergence: {summary.numIter}")
    print(f"Cluster sizes: {summary.clusterSizes}")

    print("\nFinal centroids (R, F, M):")
    for i, center in enumerate(model.clusterCenters()):
        print(f"  Cluster {i}: R={center[0]:.4f}, F={center[1]:.4f}, M={center[2]:.4f}")
    print("=" * 60)

    # Cluster Analysis
    cluster_stats = predictions \
        .groupBy("prediction") \
        .agg(
            spark_count("*").alias("user_count"),
            spark_sum("recency").alias("sum_r"),
            spark_sum("frequency").alias("sum_f"),
            spark_sum("monetary").alias("sum_m"),
        ) \
        .withColumn("avg_r", col("sum_r") / col("user_count")) \
        .withColumn("avg_f", col("sum_f") / col("user_count")) \
        .withColumn("avg_m", col("sum_m") / col("user_count")) \
        .withColumn("pct", col("user_count") / total_users * 100) \
        .orderBy("prediction")

    # Collect for segment labeling
    clusters = cluster_stats.collect()

    # Rank-based segment assignment: score = -R + F + M
    scored = []
    for row in clusters:
        score = -row["avg_r"] + row["avg_f"] + row["avg_m"]
        scored.append((score, row))
    scored.sort(key=lambda x: -x[0])  # best first

    segment_labels = [
        ("Champions", "VIP programs, loyalty rewards"),
        ("Potential Loyalists", "Personalized recommendations, upgrade incentives"),
        ("At Risk", "Win-back campaigns, special offers"),
        ("New/Casual", "Welcome series, educational content"),
    ]

    print("\n" + "=" * 80)
    print("CLUSTER ANALYSIS AND CUSTOMER SEGMENTS")
    print("=" * 80)
    print(f"{'Cluster':<10}{'Users':<10}{'%':<8}{'Avg R':<10}{'Avg F':<10}{'Avg M':<10}{'Segment':<25}{'Strategy'}")
    print("-" * 120)

    for i, (score, row) in enumerate(scored):
        segment, strategy = segment_labels[i]
        print(f"Cluster {row['prediction']:<3}{row['user_count']:<10}{row['pct']:.1f}%{'':3}"
              f"R={row['avg_r']:.4f}  F={row['avg_f']:.4f}  M={row['avg_m']:.4f}  "
              f"{segment:<25}{strategy}")

    print("=" * 80)

    # Detailed segment profiles
    print("\nSEGMENT PROFILES AND MARKETING STRATEGIES")
    print("=" * 80)
    for i, (score, row) in enumerate(scored):
        segment, strategy = segment_labels[i]
        print(f"\nCluster {row['prediction']} - \"{segment}\" ({row['pct']:.1f}% of customers):")
        print(f"  Centroid: R={row['avg_r']:.4f}, F={row['avg_f']:.4f}, M={row['avg_m']:.4f}")
        print(f"  Users: {row['user_count']:,}")
        print(f"  Strategy: {strategy}")

    # Performance comparison 
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON: MapReduce vs Spark MLlib")
    print("=" * 80)
    print(f"{'Metric':<35}{'MapReduce K-Means':<25}{'Spark MLlib K-Means'}")
    print("-" * 80)
    print(f"{'Iterations to convergence':<35}{'[From Lab 2]':<25}{summary.numIter}")
    print(f"{'Lines of core logic':<35}{'~200 (7 files)':<25}{'~50 (1 file)'}")
    print(f"{'HDFS reads per iteration':<35}{'Multiple':<25}{'1 (cached in memory)'}")
    print(f"{'Number of MapReduce jobs':<35}{'N+2 (N iterations+2)':<25}{'1 Spark job'}")
    print("=" * 80)
    print("Note: Fill in Lab 2 execution time and Spark execution time from your runs.")

    # Save results
    predictions \
        .select("user_id", "recency", "frequency", "monetary", "prediction") \
        .write.mode("overwrite").csv("/clickstream/spark_clusters/", header=True)

    print("\nCluster assignments saved to: /clickstream/spark_clusters/")

    spark.stop()


if __name__ == "__main__":
    main()
