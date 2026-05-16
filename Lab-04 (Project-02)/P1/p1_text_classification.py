from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, length, trim, regexp_replace, lower
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator


def main():
    spark = SparkSession.builder \
        .appName("Lab4_P1_TextClassification") \
        .getOrCreate()

    # Load training data
    train_df = spark.read.csv(
        "/lab4/data/train.csv",
        header=True,
        inferSchema=True,
        multiLine=True,
        escape='"'
    )

    print("DATASET OVERVIEW")
    print(f"Total training records: {train_df.count():,}")
    train_df.printSchema()

    # Preprocessing
    # Clean comment text
    cleaned_df = train_df \
        .filter(col("comment_text").isNotNull() & (length(trim(col("comment_text"))) > 0)) \
        .withColumn("comment_text",
            regexp_replace(lower(col("comment_text")), r"[^a-zA-Z\s]", " ")
        ) \
        .withColumn("comment_text",
            regexp_replace(col("comment_text"), r"\s+", " ")
        )

    # Create binary label: 1 if any of the 6 categories is 1, else 0
    label_cols = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    cleaned_df = cleaned_df.withColumn(
        "label",
        when(
            (col("toxic") == 1) | (col("severe_toxic") == 1) | (col("obscene") == 1) |
            (col("threat") == 1) | (col("insult") == 1) | (col("identity_hate") == 1),
            1.0
        ).otherwise(0.0)
    )

    # Show label distribution
    print("LABEL DISTRIBUTION")
    cleaned_df.groupBy("label").count().show()

    # Per-category counts
    print("Per-category toxic counts:")
    for lc in label_cols:
        cnt = cleaned_df.filter(col(lc) == 1).count()
        print(f"  {lc}: {cnt:,}")

    # Train/Test Split
    train_data, test_data = cleaned_df.randomSplit([0.8, 0.2], seed=42)
    print(f"\nTrain size: {train_data.count():,}")
    print(f"Test size: {test_data.count():,}")

    # Building ML Pipeline
    # Step 1: Tokenize text into words
    tokenizer = Tokenizer(inputCol="comment_text", outputCol="words")

    # Step 2: Remove stop words
    remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")

    # Step 3: HashingTF - convert words to term frequency vectors
    hashingTF = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=10000)

    # Step 4: IDF - compute inverse document frequency
    idf = IDF(inputCol="raw_features", outputCol="features")

    # Step 5: Logistic Regression classifier
    lr = LogisticRegression(maxIter=20, regParam=0.01, elasticNetParam=0.0)

    # Assemble pipeline
    pipeline = Pipeline(stages=[tokenizer, remover, hashingTF, idf, lr])

    # Train Model
    print("TRAINING MODEL...")
    model = pipeline.fit(train_data)

    # Evaluate on Test Set
    predictions = model.transform(test_data)

    # AUC-ROC
    auc_evaluator = BinaryClassificationEvaluator(
        labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC"
    )
    auc = auc_evaluator.evaluate(predictions)

    # Accuracy
    acc_evaluator = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="accuracy"
    )
    accuracy = acc_evaluator.evaluate(predictions)

    # Precision, Recall, F1
    prec_evaluator = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="weightedPrecision"
    )
    precision = prec_evaluator.evaluate(predictions)

    recall_evaluator = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="weightedRecall"
    )
    recall = recall_evaluator.evaluate(predictions)

    f1_evaluator = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="f1"
    )
    f1 = f1_evaluator.evaluate(predictions)

    print("MODEL EVALUATION RESULTS")
    print(f"AUC-ROC:            {auc:.4f}")
    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Weighted Precision: {precision:.4f}")
    print(f"Weighted Recall:    {recall:.4f}")
    print(f"F1 Score:           {f1:.4f}")

    # Confusion Matrix
    print("\nPrediction Distribution:")
    predictions.groupBy("label", "prediction").count().orderBy("label", "prediction").show()

    # Show sample predictions
    print("Sample Predictions:")
    predictions.select("comment_text", "label", "prediction", "probability") \
        .show(10, truncate=80)

    # Evaluate on Actual Test Set
    print("EVALUATING ON ACTUAL TEST SET")

    test_df = spark.read.csv(
        "/lab4/data/test.csv",
        header=True,
        inferSchema=True,
        multiLine=True,
        escape='"'
    )

    test_labels_df = spark.read.csv(
        "/lab4/data/test_labels.csv",
        header=True,
        inferSchema=True
    )

    # Filter out rows with label = -1 (not labeled)
    test_labels_clean = test_labels_df.filter(col("toxic") != -1)

    # Join test data with labels
    test_with_labels = test_df.join(test_labels_clean, "id")

    # Apply same preprocessing
    test_with_labels = test_with_labels \
        .filter(col("comment_text").isNotNull() & (length(trim(col("comment_text"))) > 0)) \
        .withColumn("comment_text",
            regexp_replace(lower(col("comment_text")), r"[^a-zA-Z\s]", " ")
        ) \
        .withColumn("comment_text",
            regexp_replace(col("comment_text"), r"\s+", " ")
        ) \
        .withColumn("label",
            when(
                (col("toxic") == 1) | (col("severe_toxic") == 1) | (col("obscene") == 1) |
                (col("threat") == 1) | (col("insult") == 1) | (col("identity_hate") == 1),
                1.0
            ).otherwise(0.0)
        )

    print(f"Test records (labeled): {test_with_labels.count():,}")

    # Predict on test set
    test_predictions = model.transform(test_with_labels)

    test_auc = auc_evaluator.evaluate(test_predictions)
    test_accuracy = acc_evaluator.evaluate(test_predictions)
    test_f1 = f1_evaluator.evaluate(test_predictions)

    print(f"Test AUC-ROC:  {test_auc:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"Test F1 Score: {test_f1:.4f}")

    # Save predictions
    predictions.select("id", "comment_text", "label", "prediction") \
        .write.mode("overwrite").csv("/lab4/output/predictions/", header=True)

    # Save model
    model.write().overwrite().save("/lab4/output/model/")

    print(f"\nPredictions saved to: /lab4/output/predictions/")
    print(f"Model saved to: /lab4/output/model/")

    spark.stop()


if __name__ == "__main__":
    main()
