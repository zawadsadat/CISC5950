from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, mean as spark_mean, count as spark_count
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator


def main():
    spark = SparkSession.builder \
        .appName("Lab4_P2_HeartDisease") \
        .getOrCreate()

    # Load Framingham dataset (read as strings to handle NA values)
    raw_df = spark.read.csv(
        "/lab4/data/framingham.csv",
        header=True,
        inferSchema=False
    )

    print("DATASET OVERVIEW")
    print(f"{'='*60}")
    total = raw_df.count()
    print(f"Total records: {total}")
    print(f"Columns: {len(raw_df.columns)}")

    # Drop 'education' column (as per sample code)
    df = raw_df.drop("education")

    # Handle missing values
    # Replace "NA" strings with null first
    all_cols = df.columns
    for c in all_cols:
        df = df.withColumn(c, when((col(c) == "NA") | (col(c) == ""), None).otherwise(col(c)))

    # Count missing values per column
    print("MISSING VALUES PER COLUMN")
    feature_cols = [c for c in df.columns if c != "TenYearCHD"]
    for c in feature_cols:
        null_count = df.filter(col(c).isNull()).count()
        if null_count > 0:
            print(f"  {c}: {null_count} ({null_count/total*100:.1f}%)")

    # Cast all columns to double
    for c in all_cols:
        df = df.withColumn(c, col(c).cast("double"))

    # Drop rows with any null values (as per sample code approach)
    df_clean = df.dropna()
    clean_count = df_clean.count()
    dropped = total - clean_count
    print(f"\nTotal rows with missing values: {dropped}")
    print(f"Since it is only {dropped/total*100:.1f}% of the entire dataset, rows with missing values are excluded.")
    print(f"Clean dataset size: {clean_count}")

    # Label distribution
    print("LABEL DISTRIBUTION (TenYearCHD)")
    df_clean.groupBy("TenYearCHD").count().show()

    # Prepare features
    feature_cols = [c for c in df_clean.columns if c != "TenYearCHD"]
    print(f"Feature columns ({len(feature_cols)}): {feature_cols}")

    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="features"
    )
    data = assembler.transform(df_clean).select("features", col("TenYearCHD").alias("label"))

    # Train/Test Split
    train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)
    print(f"\nTrain size: {train_data.count()}")
    print(f"Test size: {test_data.count()}")

    # Train Logistic Regression
    print("TRAINING LOGISTIC REGRESSION MODEL")

    lr = LogisticRegression(
        maxIter=100,
        regParam=0.01,
        elasticNetParam=0.0,
        labelCol="label",
        featuresCol="features"
    )
    model = lr.fit(train_data)

    # Model Summary
    print(f"\nCoefficients: {model.coefficients}")
    print(f"Intercept: {model.intercept}")

    # Identify most important risk factors
    coeff_list = list(zip(feature_cols, model.coefficients.toArray()))
    coeff_list.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f"\nTop Risk Factors (by coefficient magnitude):")
    for feat, coeff in coeff_list[:5]:
        direction = "increases" if coeff > 0 else "decreases"
        print(f"  {feat}: {coeff:.4f} ({direction} risk)")

    # Evaluate on Test Set
    predictions = model.transform(test_data)

    # AUC-ROC
    auc_eval = BinaryClassificationEvaluator(
        labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC"
    )
    auc = auc_eval.evaluate(predictions)

    # Accuracy
    acc_eval = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="accuracy"
    )
    accuracy = acc_eval.evaluate(predictions)

    # Precision
    prec_eval = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="weightedPrecision"
    )
    precision = prec_eval.evaluate(predictions)

    # Recall
    rec_eval = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="weightedRecall"
    )
    recall = rec_eval.evaluate(predictions)

    # F1
    f1_eval = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="f1"
    )
    f1 = f1_eval.evaluate(predictions)

    print("MODEL EVALUATION RESULTS")
    print(f"AUC-ROC:            {auc:.4f}")
    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Weighted Precision: {precision:.4f}")
    print(f"Weighted Recall:    {recall:.4f}")
    print(f"F1 Score:           {f1:.4f}")
 
    # Confusion Matrix
    print("\nConfusion Matrix:")
    predictions.groupBy("label", "prediction").count().orderBy("label", "prediction").show()

    # Save predictions
    predictions.select("label", "prediction") \
        .write.mode("overwrite").csv("/lab4/output/p2_predictions/", header=True)

    print(f"Predictions saved to: /lab4/output/p2_predictions/")

    spark.stop()


if __name__ == "__main__":
    main()
