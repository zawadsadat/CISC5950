from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, when, regexp_replace
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator


def build_schema():
    """14 attributes + income label, all read as strings."""
    names = ["age", "workclass", "fnlwgt", "education", "education_num",
             "marital_status", "occupation", "relationship", "race", "sex",
             "capital_gain", "capital_loss", "hours_per_week", "native_country", "income"]
    return StructType([StructField(n, StringType(), True) for n in names])


def load_and_clean(spark, path, skip_first_line=False):
    """Load CSV, trim whitespace, handle test file quirks."""
    schema = build_schema()

    if skip_first_line:
        # adult.test has a junk first line
        rdd = spark.sparkContext.textFile(path)
        rdd = rdd.zipWithIndex().filter(lambda x: x[1] > 0).keys()
        df = spark.read.csv(rdd, schema=schema)
    else:
        df = spark.read.csv(path, schema=schema)

    # Trim whitespace from all columns
    for c in df.columns:
        df = df.withColumn(c, trim(col(c)))

    # Remove trailing period from income in test set (<=50K. -> <=50K)
    df = df.withColumn("income", regexp_replace(col("income"), r"\.$", ""))

    # Filter out rows with missing values marked as "?"
    for c in df.columns:
        df = df.filter(col(c) != "?")

    # Cast numeric columns
    numeric_cols = ["age", "fnlwgt", "education_num", "capital_gain",
                    "capital_loss", "hours_per_week"]
    for c in numeric_cols:
        df = df.withColumn(c, col(c).cast("double"))

    # Create binary label: 1 for >50K, 0 for <=50K
    df = df.withColumn("label", when(col("income") == ">50K", 1.0).otherwise(0.0))

    return df


def build_pipeline(classifier, classifier_name="Classifier"):
    """Build ML pipeline with feature engineering + classifier."""
    categorical_cols = ["workclass", "education", "marital_status", "occupation",
                        "relationship", "race", "sex", "native_country"]
    numeric_cols = ["age", "fnlwgt", "education_num", "capital_gain",
                    "capital_loss", "hours_per_week"]

    # Index categorical columns
    indexers = [StringIndexer(inputCol=c, outputCol=c+"_idx", handleInvalid="skip")
                for c in categorical_cols]

    # One-hot encode indexed columns
    encoders = [OneHotEncoder(inputCol=c+"_idx", outputCol=c+"_vec")
                for c in categorical_cols]

    # Assemble all features
    feature_cols = numeric_cols + [c+"_vec" for c in categorical_cols]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features",
                                handleInvalid="skip")

    pipeline = Pipeline(stages=indexers + encoders + [assembler, classifier])
    return pipeline


def evaluate_model(predictions, model_name):
    """Print evaluation metrics."""
    auc_eval = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
    acc_eval = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    prec_eval = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="weightedPrecision")
    rec_eval = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="weightedRecall")
    f1_eval = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")

    auc = auc_eval.evaluate(predictions)
    accuracy = acc_eval.evaluate(predictions)
    precision = prec_eval.evaluate(predictions)
    recall = rec_eval.evaluate(predictions)
    f1 = f1_eval.evaluate(predictions)

    print(f"{model_name} - EVALUATION RESULTS")
    print(f"AUC-ROC:            {auc:.4f}")
    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Weighted Precision: {precision:.4f}")
    print(f"Weighted Recall:    {recall:.4f}")
    print(f"F1 Score:           {f1:.4f}")

    print(f"\nConfusion Matrix ({model_name}):")
    predictions.groupBy("label", "prediction").count().orderBy("label", "prediction").show()

    return {"auc": auc, "accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


def main():
    spark = SparkSession.builder \
        .appName("Lab4_P3_CensusIncome_LR") \
        .getOrCreate()

    # Load data
    train_df = load_and_clean(spark, "/lab4/data/adult.data", skip_first_line=False)
    test_df = load_and_clean(spark, "/lab4/data/adult.test", skip_first_line=True)

    print("DATASET OVERVIEW")
    print(f"Training records: {train_df.count():,}")
    print(f"Test records: {test_df.count():,}")

    print("\nLabel distribution (train):")
    train_df.groupBy("income").count().show()

    print("Label distribution (test):")
    test_df.groupBy("income").count().show()

    # Build and train Logistic Regression
    lr = LogisticRegression(maxIter=100, regParam=0.01, elasticNetParam=0.0,
                            labelCol="label", featuresCol="features")
    pipeline = build_pipeline(lr, "Logistic Regression")

    print("Training Logistic Regression...")
    model = pipeline.fit(train_df)

    # Evaluate on test set
    predictions = model.transform(test_df)
    evaluate_model(predictions, "LOGISTIC REGRESSION")

    # Save predictions
    predictions.select("label", "prediction") \
        .write.mode("overwrite").csv("/lab4/output/p3_predictions/", header=True)
    print("Predictions saved to: /lab4/output/p3_predictions/")

    spark.stop()


if __name__ == "__main__":
    main()
