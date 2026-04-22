from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    broadcast, desc, col, trim, upper, when,
    sum as spark_sum, count as spark_count,
    coalesce, lit, regexp_extract
)
from pyspark.sql.types import IntegerType


def extract_year_from_date(date_col):
    """Extract year from date string (MM/DD/YYYY or YYYY-MM-DD)."""
    trimmed = trim(date_col)
    return (
        when(trimmed.contains("/"),
             regexp_extract(trimmed, r"\d+/\d+/(\d{4})", 1))
        .otherwise(trimmed.substr(1, 4))
    )


def main():
    spark = SparkSession.builder \
        .appName("Lab3_Task1_2_Hotspots") \
        .getOrCreate()

    # Read cleaned data from Task 1.1
    try:
        cleaned_df = spark.read.csv("/parking/spark_clean/", header=True, inferSchema=False)
        print("Reading from /parking/spark_clean/")
    except Exception:
        # Fall back to reading raw and applying minimal cleaning
        print("spark_clean not found, reading from /parking/raw/")
        raw_df = spark.read.csv("/parking/raw/*", header=True, inferSchema=False, quote='"', escape='"')
        cleaned_df = raw_df \
            .withColumn("_year", extract_year_from_date(col("Issue Date"))) \
            .filter(
                col("Plate ID").isNotNull() & (trim(col("Plate ID")) != "") &
                col("Violation Code").isNotNull() & (trim(col("Violation Code")) != "") &
                col("Issue Date").isNotNull() & (trim(col("Issue Date")) != "") &
                col("_year").isin("2024", "2025")
            ) \
            .drop("_year")

    # Create fine amount lookup DataFrame
    fines_data = [
        ("5", 35), ("7", 35), ("12", 45), ("14", 115), ("15", 115),
        ("16", 115), ("17", 65), ("19", 115), ("20", 65), ("21", 45),
        ("31", 115), ("36", 50), ("37", 65), ("38", 35), ("40", 115),
        ("43", 35), ("46", 115), ("47", 65), ("48", 115), ("50", 115),
        ("69", 65), ("70", 65), ("71", 65), ("74", 65), ("75", 115),
        ("78", 65), ("84", 65), ("98", 115),
    ]
    fines_df = spark.createDataFrame(fines_data, ["violation_code", "fine_amount"])

    # Broadcast join
    # Normalize violation code for join
    cleaned_with_code = cleaned_df.withColumn(
        "violation_code_clean", trim(col("Violation Code"))
    )

    revenue_df = cleaned_with_code.join(
        broadcast(fines_df),
        cleaned_with_code["violation_code_clean"] == fines_df["violation_code"],
        "left"
    ).withColumn(
        "fine_amount", coalesce(col("fine_amount"), lit(50))  # default $50
    )

    # Top-20 hotspot aggregation
    # Use Street Code1 and Street Name for location identification
    hotspots_df = revenue_df \
        .withColumn("street_code", trim(col("Street Code1"))) \
        .withColumn("street_name", trim(col("Street Name"))) \
        .filter(
            (col("street_code").isNotNull()) & (col("street_code") != "") &
            (col("street_name").isNotNull()) & (col("street_name") != "")
        ) \
        .groupBy("street_code", "street_name") \
        .agg(
            spark_count("*").alias("total_tickets"),
            spark_sum("fine_amount").alias("total_revenue"),
            (spark_count("*") / 365.0).alias("tickets_per_day")
        ) \
        .orderBy(desc("total_tickets")) \
        .limit(20)

    # Display and save results
    print("\n" + "=" * 80)
    print("TOP 20 GEOGRAPHIC HOTSPOTS")
    print("=" * 80)
    hotspots_df.show(20, truncate=False)

    # Collect and print formatted table
    rows = hotspots_df.collect()
    print(f"{'Rank':<6}{'Street Code':<14}{'Street Name':<30}{'Tickets':<12}{'Est Revenue':<14}{'Tickets/Day':<12}")
    print("-" * 88)
    for i, row in enumerate(rows, 1):
        print(f"{i:<6}{row['street_code']:<14}{row['street_name']:<30}{row['total_tickets']:<12}${row['total_revenue']:,.0f}{'':<2}{row['tickets_per_day']:<12.1f}")

    # Calculate totals for recommendation
    total_all = revenue_df.count()
    top10_tickets = sum(row['total_tickets'] for row in rows[:10])
    top10_revenue = sum(row['total_revenue'] for row in rows[:10])
    top10_pct = top10_tickets / total_all * 100

    print(f"\n{'=' * 80}")
    print("ENFORCEMENT RESOURCE ALLOCATION RECOMMENDATION")
    print(f"{'=' * 80}")
    print(f"Total violations in dataset: {total_all:,}")
    print(f"Top 10 locations: {top10_tickets:,} tickets ({top10_pct:.1f}% of total)")
    print(f"Top 10 estimated revenue: ${top10_revenue:,.0f}")
    print(f"\nRecommendation: Deploy 40% of enforcement officers to the top 10 locations")
    print(f"to capture {top10_pct:.1f}% of all violations.")
    print(f"{'=' * 80}")

    # Save results
    hotspots_df.write.mode("overwrite").csv("/parking/hotspots/", header=True)
    print("\nOutput saved to: /parking/hotspots/")

    spark.stop()


if __name__ == "__main__":
    main()
