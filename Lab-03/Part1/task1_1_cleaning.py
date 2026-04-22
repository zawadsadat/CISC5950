from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import (
    when, col, upper, trim, regexp_extract, lit, count as spark_count
)


def build_schema():
    """Define explicit schema for the 43-column parking violations CSV."""
    fields = [
        ("Summons Number", StringType()),
        ("Plate ID", StringType()),
        ("Registration State", StringType()),
        ("Plate Type", StringType()),
        ("Issue Date", StringType()),
        ("Violation Code", StringType()),
        ("Vehicle Body Type", StringType()),
        ("Vehicle Make", StringType()),
        ("Issuing Agency", StringType()),
        ("Street Code1", StringType()),
        ("Street Code2", StringType()),
        ("Street Code3", StringType()),
        ("Vehicle Expiration Date", StringType()),
        ("Violation Location", StringType()),
        ("Violation Precinct", StringType()),
        ("Issuer Precinct", StringType()),
        ("Issuer Code", StringType()),
        ("Issuer Command", StringType()),
        ("Issuer Squad", StringType()),
        ("Violation Time", StringType()),
        ("Time First Observed", StringType()),
        ("Violation County", StringType()),
        ("Violation In Front Of Or Opposite", StringType()),
        ("House Number", StringType()),
        ("Street Name", StringType()),
        ("Intersecting Street", StringType()),
        ("Date First Observed", StringType()),
        ("Law Section", StringType()),
        ("Sub Division", StringType()),
        ("Violation Legal Code", StringType()),
        ("Days Parking In Effect", StringType()),
        ("From Hours In Effect", StringType()),
        ("To Hours In Effect", StringType()),
        ("Vehicle Color", StringType()),
        ("Unregistered Vehicle?", StringType()),
        ("Vehicle Year", StringType()),
        ("Meter Number", StringType()),
        ("Feet From Curb", StringType()),
        ("Violation Post Code", StringType()),
        ("Violation Description", StringType()),
        ("No Standing or Stopping Violation", StringType()),
        ("Hydrant Violation", StringType()),
        ("Double Parking Violation", StringType()),
    ]
    return StructType([StructField(name, dtype, True) for name, dtype in fields])


def normalize_color(color_col):
    """Build a chained when() expression for color normalization."""
    c = upper(trim(color_col))
    return (
        when(c.isin("BLK", "BLACK", "BK"), "BLACK")
        .when(c.isin("WH", "WHT", "WHITE", "WT", "WHI", "WHBK"), "WHITE")
        .when(c.isin("GRY", "GRAY", "GREY", "GY", "GR", "LTGY", "GRGY", "BLGY", "DKGY"), "GRAY")
        .when(c.isin("BL", "BLU", "BLUE", "BLW"), "BLUE")
        .when(c.isin("RED", "RD"), "RED")
        .when(c.isin("GREEN", "GRN", "GN", "GL", "DKG"), "GREEN")
        .when(c.isin("SILVER", "SIL", "SLV", "SILV", "SILVE"), "SILVER")
        .when(c.isin("BROWN", "BRN", "BR", "LTBR"), "BROWN")
        .when(c.isin("TAN", "TN"), "TAN")
        .when(c.isin("YELLOW", "YL", "YEL", "YELL", "YW", "YELLO"), "YELLOW")
        .when(c.isin("BEIGE", "BG"), "BEIGE")
        .when(c.isin("ORANGE", "ORG", "ORANG", "OR"), "ORANGE")
        .when(c.isin("PURPLE", "PR"), "PURPLE")
        .when(c.isin("MAROON", "MR"), "MAROON")
        .when(c.isin("GOLD", "GLD"), "GOLD")
        .when(c.isin("PINK", "PK"), "PINK")
        .when(c.isin("UNKNOWN", "UNK", "UNKNO"), "UNKNOWN")
        .when(c.isin("BKWH"), "BLACK")
        .when(c.isin("OTHER"), "OTHER")
        .otherwise(c)
    )


def normalize_state(state_col):
    """Build a chained when() expression for state normalization."""
    s = upper(trim(state_col))
    return (
        when(s.isin("NY", "NEW YORK", "N Y"), "NY")
        .when(s.isin("NJ", "NEW JERSEY"), "NJ")
        .when(s.isin("PA", "PENNSYLVANIA"), "PA")
        .when(s.isin("CT", "CONNECTICUT"), "CT")
        .when(s.isin("MA", "MASSACHUSETTS"), "MA")
        .when(s.isin("FL", "FLORIDA"), "FL")
        .when(s.isin("CA", "CALIFORNIA"), "CA")
        .when(s.isin("TX", "TEXAS"), "TX")
        .when(s.isin("VA", "VIRGINIA"), "VA")
        .when(s.isin("MD", "MARYLAND"), "MD")
        .when(s.isin("DC", "DISTRICT OF COLUMBIA"), "DC")
        .otherwise(s)
    )


def extract_hour(vtime_col):
    """
    Extract hour (0-23) from violation_time like '0209P' or '1105A'.
    Uses regexp_extract to pull digits and AM/PM indicator.
    Returns null for malformed or empty values.
    """
    raw = upper(trim(vtime_col))
    hh_str = regexp_extract(raw, r"^(\d{2})\d{2}[AP]$", 1)
    ampm = regexp_extract(raw, r"^\d{4}([AP])$", 1)

    # Only cast to int when we have a valid match (non-empty string)
    hh = when(hh_str != "", hh_str.cast(IntegerType())).otherwise(lit(None).cast(IntegerType()))

    return (
        when(hh.isNull() | (ampm == ""), lit(None).cast(IntegerType()))
        .when((ampm == "A") & (hh == 12), lit(0))
        .when(ampm == "A", hh)
        .when((ampm == "P") & (hh == 12), lit(12))
        .when(ampm == "P", hh + 12)
        .otherwise(lit(None).cast(IntegerType()))
    )


def extract_year_from_date(date_col):
    """
    Extract year from date string. Handles both:
    - MM/DD/YYYY  -> split on '/', take 3rd part
    - YYYY-MM-DD... -> first 4 chars
    """
    trimmed = trim(date_col)
    return (
        when(trimmed.contains("/"),
             regexp_extract(trimmed, r"\d+/\d+/(\d{4})", 1))
        .otherwise(trimmed.substr(1, 4))
    )


def main():
    spark = SparkSession.builder \
        .appName("Lab3_Task1_1_DataCleaning") \
        .getOrCreate()

    # Read raw data with explicit schema
    schema = build_schema()
    raw_df = spark.read.csv(
        "/parking/raw/*",
        header=True,
        schema=schema,
        quote='"',
        escape='"'
    )

    total_input = raw_df.count()
    print(f"\n=== Total input records: {total_input} ===\n")

    # Unified cleaning pipeline

    # Step 1: Extract year for date validation
    with_year = raw_df.withColumn("_year", extract_year_from_date(col("Issue Date")))

    # Step 2: Tag records for quality report before filtering
    tagged = with_year \
        .withColumn("_has_critical",
                     col("Plate ID").isNotNull() & (trim(col("Plate ID")) != "") &
                     col("Violation Code").isNotNull() & (trim(col("Violation Code")) != "") &
                     col("Issue Date").isNotNull() & (trim(col("Issue Date")) != "")) \
        .withColumn("_valid_date",
                     col("_year").isin("2024", "2025"))

    # Quality Report (before filtering)
    missing_critical = tagged.filter(~col("_has_critical")).count()
    has_critical_df = tagged.filter(col("_has_critical"))
    invalid_date = has_critical_df.filter(~col("_valid_date")).count()
    valid_records = has_critical_df.filter(col("_valid_date")).count()

    # Count color and state corrections on valid records
    valid_df = has_critical_df.filter(col("_valid_date"))

    color_raw = upper(trim(col("Vehicle Color")))
    color_corrections = valid_df.filter(
        (col("Vehicle Color").isNotNull()) & (trim(col("Vehicle Color")) != "") &
        (normalize_color(col("Vehicle Color")) != color_raw)
    ).count()

    state_raw = upper(trim(col("Registration State")))
    state_corrections = valid_df.filter(
        (col("Registration State").isNotNull()) & (trim(col("Registration State")) != "") &
        (normalize_state(col("Registration State")) != state_raw)
    ).count()

    print("=" * 50)
    print("DATA QUALITY REPORT")
    print("=" * 50)
    print(f"TOTAL_INPUT\t{total_input}")
    print(f"VALID_OUTPUT_RECORDS\t{valid_records}\t({valid_records/total_input*100:.1f}%)")
    print(f"INVALID_DATE_RECORDS\t{invalid_date}\t({invalid_date/total_input*100:.3f}%)")
    print(f"MISSING_CRITICAL_FIELDS\t{missing_critical}\t({missing_critical/total_input*100:.3f}%)")
    print(f"COLOR_STANDARDIZATIONS\t{color_corrections}\t({color_corrections/total_input*100:.1f}%)")
    print(f"STATE_CODE_CORRECTIONS\t{state_corrections}\t({state_corrections/total_input*100:.3f}%)")
    print("=" * 50)

    # Apply cleaning transformations
    cleaned_df = valid_df \
        .withColumn("Registration State", normalize_state(col("Registration State"))) \
        .withColumn("Vehicle Color", normalize_color(col("Vehicle Color"))) \
        .withColumn("hour_of_day", extract_hour(col("Violation Time"))) \
        .drop("_year", "_has_critical", "_valid_date")

    # Write cleaned output
    cleaned_df.write.mode("overwrite").csv("/parking/spark_clean/", header=True)

    print(f"\nCleaned records written: {valid_records}")
    print("Output: /parking/spark_clean/")

    spark.stop()


if __name__ == "__main__":
    main()
