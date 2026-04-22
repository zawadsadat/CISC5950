from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import (
    lag, when, col, trim, to_timestamp, try_to_timestamp,
    sum as spark_sum, min as spark_min, max as spark_max,
    count as spark_count, lit, dayofyear, abs as spark_abs, coalesce
)


def main():
    spark = SparkSession.builder \
        .appName("Lab3_Task2_1_Sessions") \
        .getOrCreate()

    # Read raw clickstream data
    raw_df = spark.read.csv(
        "/clickstream/raw/*",
        header=True,
        inferSchema=False
    )

    # Parse timestamp - try multiple formats, tolerate invalid values
    events_df = raw_df \
        .withColumn("ts",
            coalesce(
                try_to_timestamp(col("timestamp"), lit("M/d/yyyy H:mm:ss")),
                try_to_timestamp(col("timestamp"), lit("M/d/yyyy H:mm")),
                try_to_timestamp(col("timestamp"), lit("yyyy-MM-dd HH:mm:ss")),
                try_to_timestamp(col("timestamp"), lit("yyyy-MM-dd'T'HH:mm:ss")),
            )
        ) \
        .filter(col("ts").isNotNull()) \
        .withColumn("user_id", trim(col("user_id"))) \
        .withColumn("event_type", trim(col("event_type"))) \
        .withColumn("price",
            when(trim(col("price")) == "", lit(0.0))
            .otherwise(col("price").cast("double"))
        ) \
        .withColumn("device_type", trim(col("device_type"))) \
        .withColumn("traffic_source", trim(col("traffic_source")))

    # Window function for session reconstruction 
    # Partition by user, order by timestamp
    window_spec = Window.partitionBy("user_id").orderBy("ts")

    # Calculate time gap from previous event (in minutes)
    with_gaps = events_df \
        .withColumn("prev_ts", lag("ts").over(window_spec)) \
        .withColumn("time_gap_minutes",
            (col("ts").cast("long") - col("prev_ts").cast("long")) / 60.0
        ) \
        .withColumn("prev_day", dayofyear(col("prev_ts"))) \
        .withColumn("curr_day", dayofyear(col("ts")))

    # Mark new session boundaries:
    # 1. First event for a user (no previous event)
    # 2. Gap > 30 minutes
    # 3. Midnight crossing (different day)
    with_flags = with_gaps \
        .withColumn("new_session",
            when(col("prev_ts").isNull(), lit(1))
            .when(col("time_gap_minutes") > 30, lit(1))
            .when(col("curr_day") != col("prev_day"), lit(1))
            .otherwise(lit(0))
        )

    # Assign session IDs using cumulative sum of new_session flags
    cum_window = Window.partitionBy("user_id").orderBy("ts") \
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)

    with_sessions = with_flags \
        .withColumn("session_num", spark_sum("new_session").over(cum_window))

    # Aggregate session-level metrics
    session_metrics = with_sessions \
        .groupBy("user_id", "session_num") \
        .agg(
            spark_min("ts").alias("start_time"),
            spark_max("ts").alias("end_time"),
            spark_count("*").alias("event_count"),
            spark_sum(
                when(col("event_type") == "purchase", col("price")).otherwise(0.0)
            ).alias("total_revenue"),
            spark_max(
                when(col("event_type") == "view", lit(1)).otherwise(lit(0))
            ).alias("has_view"),
            spark_max(
                when(col("event_type").isin("addtocart", "add_to_cart", "cart"), lit(1)).otherwise(lit(0))
            ).alias("has_cart"),
            spark_max(
                when(col("event_type") == "purchase", lit(1)).otherwise(lit(0))
            ).alias("has_purchase"),
            spark_min("device_type").alias("device_type"),
            spark_min("traffic_source").alias("traffic_source"),
        ) \
        .withColumn("duration_minutes",
            (col("end_time").cast("long") - col("start_time").cast("long")) / 60.0
        ) \
        .withColumn("converted", col("total_revenue") > 0)

    # Cache for reuse
    session_metrics.cache()

    # Compute summary metrics
    total_sessions = session_metrics.count()
    avg_duration = session_metrics.agg({"duration_minutes": "avg"}).collect()[0][0]
    avg_events = session_metrics.agg({"event_count": "avg"}).collect()[0][0]
    converted_count = session_metrics.filter(col("converted")).count()
    conversion_rate = converted_count / total_sessions * 100 if total_sessions > 0 else 0
    avg_rev_converted = session_metrics.filter(col("converted")) \
        .agg({"total_revenue": "avg"}).collect()[0][0]

    print("\n" + "=" * 60)
    print("SESSION SUMMARY METRICS")
    print("=" * 60)
    print(f"Total sessions reconstructed: {total_sessions:,}")
    print(f"Average session duration: {avg_duration:.1f} minutes")
    print(f"Conversion rate: {conversion_rate:.1f}%")
    print(f"Average events per session: {avg_events:.1f}")
    if avg_rev_converted:
        print(f"Average revenue per converted session: ${avg_rev_converted:.2f}")
    print("=" * 60)

    # Golden Session Pattern Analysis
    # Find characteristics of sessions with highest conversion rates
    print("\n" + "=" * 60)
    print("GOLDEN SESSION PATTERN ANALYSIS")
    print("=" * 60)

    # Conversion rate by device
    print("\nConversion rate by device type:")
    session_metrics.groupBy("device_type") \
        .agg(
            spark_count("*").alias("sessions"),
            spark_sum(when(col("converted"), 1).otherwise(0)).alias("converted"),
        ) \
        .withColumn("conv_rate", (col("converted") / col("sessions") * 100)) \
        .orderBy(col("conv_rate").desc()) \
        .show(truncate=False)

    # Conversion rate by traffic source
    print("Conversion rate by traffic source:")
    session_metrics.groupBy("traffic_source") \
        .agg(
            spark_count("*").alias("sessions"),
            spark_sum(when(col("converted"), 1).otherwise(0)).alias("converted"),
        ) \
        .withColumn("conv_rate", (col("converted") / col("sessions") * 100)) \
        .orderBy(col("conv_rate").desc()) \
        .show(truncate=False)

    # Conversion rate by duration bucket
    print("Conversion rate by duration bucket:")
    session_metrics \
        .withColumn("duration_bucket",
            when(col("duration_minutes") <= 5, "0-5 min")
            .when(col("duration_minutes") <= 15, "5-15 min")
            .when(col("duration_minutes") <= 30, "15-30 min")
            .when(col("duration_minutes") <= 60, "30-60 min")
            .otherwise("60+ min")
        ) \
        .groupBy("duration_bucket") \
        .agg(
            spark_count("*").alias("sessions"),
            spark_sum(when(col("converted"), 1).otherwise(0)).alias("converted"),
        ) \
        .withColumn("conv_rate", (col("converted") / col("sessions") * 100)) \
        .orderBy(col("conv_rate").desc()) \
        .show(truncate=False)

    # Save session output
    session_metrics \
        .select(
            "user_id", "session_num", "start_time", "end_time",
            "duration_minutes", "event_count", "converted",
            "total_revenue", "device_type", "traffic_source",
            "has_view", "has_cart", "has_purchase"
        ) \
        .write.mode("overwrite").csv("/clickstream/spark_sessions/", header=True)

    print("\nSession output saved to: /clickstream/spark_sessions/")

    # Show sample sessions
    print("\nSample sessions:")
    session_metrics.select(
        "user_id", "session_num", "start_time", "end_time",
        "duration_minutes", "event_count", "converted", "total_revenue"
    ).show(10, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
