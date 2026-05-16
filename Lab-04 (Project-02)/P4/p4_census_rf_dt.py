from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassifier, DecisionTreeClassifier

# Import shared functions from P3
import sys
sys.path.insert(0, "/spark-examples/test-python/lab4/P3")
from p3_census_lr import load_and_clean, build_pipeline, evaluate_model


def main():
    spark = SparkSession.builder \
        .appName("Lab4_P4_CensusIncome_RF_DT") \
        .getOrCreate()

    # Load data (same as P3)
    train_df = load_and_clean(spark, "/lab4/data/adult.data", skip_first_line=False)
    test_df = load_and_clean(spark, "/lab4/data/adult.test", skip_first_line=True)

    print("DATASET OVERVIEW")
    print(f"Training records: {train_df.count():,}")
    print(f"Test records: {test_df.count():,}")

    # Random Forest Classifier
    print("TRAINING RANDOM FOREST CLASSIFIER")


    rf = RandomForestClassifier(
        numTrees=100,
        maxDepth=10,
        seed=42,
        labelCol="label",
        featuresCol="features"
    )
    rf_pipeline = build_pipeline(rf, "Random Forest")
    rf_model = rf_pipeline.fit(train_df)
    rf_predictions = rf_model.transform(test_df)
    rf_metrics = evaluate_model(rf_predictions, "RANDOM FOREST")

    # Feature importance
    rf_stage = rf_model.stages[-1]
    print("Feature Importances (top 10):")
    importances = rf_stage.featureImportances.toArray()
    # Get feature names from assembler
    assembler_stage = rf_model.stages[-2]
    feat_names = assembler_stage.getInputCols()
    feat_imp = sorted(zip(feat_names, importances), key=lambda x: -x[1])
    for name, imp in feat_imp[:10]:
        print(f"  {name}: {imp:.4f}")

    rf_predictions.select("label", "prediction") \
        .write.mode("overwrite").csv("/lab4/output/p4_rf_predictions/", header=True)

    # Decision Tree Classifier
    print("TRAINING DECISION TREE CLASSIFIER")


    dt = DecisionTreeClassifier(
        maxDepth=10,
        seed=42,
        labelCol="label",
        featuresCol="features"
    )
    dt_pipeline = build_pipeline(dt, "Decision Tree")
    dt_model = dt_pipeline.fit(train_df)
    dt_predictions = dt_model.transform(test_df)
    dt_metrics = evaluate_model(dt_predictions, "DECISION TREE")

    dt_predictions.select("label", "prediction") \
        .write.mode("overwrite").csv("/lab4/output/p4_dt_predictions/", header=True)

    # Comparison Summary
    print("MODEL COMPARISON SUMMARY")
    print(f"{'Metric':<25}{'Random Forest':<20}{'Decision Tree':<20}")
    print(f"{'AUC-ROC':<25}{rf_metrics['auc']:<20.4f}{dt_metrics['auc']:<20.4f}")
    print(f"{'Accuracy':<25}{rf_metrics['accuracy']:<20.4f}{dt_metrics['accuracy']:<20.4f}")
    print(f"{'Weighted Precision':<25}{rf_metrics['precision']:<20.4f}{dt_metrics['precision']:<20.4f}")
    print(f"{'Weighted Recall':<25}{rf_metrics['recall']:<20.4f}{dt_metrics['recall']:<20.4f}")
    print(f"{'F1 Score':<25}{rf_metrics['f1']:<20.4f}{dt_metrics['f1']:<20.4f}")

    print("\nPredictions saved to:")
    print("  Random Forest: /lab4/output/p4_rf_predictions/")
    print("  Decision Tree: /lab4/output/p4_dt_predictions/")

    spark.stop()


if __name__ == "__main__":
    main()
