#Train_2025.py
import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
import optuna
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print(" 🚀 TRAINING MODEL 2025 - WITH DETAILED REPORTING")
print("="*70)

# Create reports directory
os.makedirs("Models/2025/reports", exist_ok=True)

# ---------------------------------------------------
# STEP 1: Load data
# ---------------------------------------------------
print("\n📥 Loading data...")
X = joblib.load("features_2025.pkl")
y = joblib.load("labels_2025.pkl")
print(f"✅ Features loaded: {X.shape}")
print(f"✅ Labels loaded: {len(y)}")

# ---------------------------------------------------
# STEP 2: Validate labels
# ---------------------------------------------------
print("\n🔍 Validating labels...")
y = pd.Series(y)

if y.isnull().any():
    missing_count = y.isnull().sum()
    print(f"⚠️  WARNING: {missing_count} missing labels detected!")
    valid_indices = ~y.isnull()
    X = X[valid_indices]
    y = y[valid_indices]
    print(f"✅ After cleaning: {len(y)} samples remain")

if y.dtype == 'object':
    label_mapping = {'Legitimate': 0, 'Phishing': 1}
    y = y.map(label_mapping)
    if y.isnull().any():
        print("❌ ERROR: Some labels couldn't be mapped!")
        raise ValueError("Invalid label format")
else:
    if not set(y.unique()).issubset({0, 1}):
        print("❌ ERROR: Numeric labels must be 0 or 1")
        raise ValueError(f"Invalid numeric labels: {y.unique()}")

y = y.values

print(f"✅ Label distribution:")
unique, counts = np.unique(y, return_counts=True)
label_distribution = {}
for label, count in zip(unique, counts):
    label_name = 'Legitimate' if label == 0 else 'Phishing'
    label_distribution[label_name] = int(count)
    print(f"   {label_name}: {count} ({count/len(y)*100:.1f}%)")

# ---------------------------------------------------
# STEP 3: Train-test split
# ---------------------------------------------------
print("\n📊 Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✅ Training set: {X_train.shape[0]} samples")
print(f"✅ Test set: {X_test.shape[0]} samples")

# ---------------------------------------------------
# STEP 4: Hyperparameter optimization
# ---------------------------------------------------
print("\n🔍 Starting hyperparameter optimization...")

def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 200, 600),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "gamma": trial.suggest_float("gamma", 0.0, 0.5),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 5.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 5.0),
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "random_state": 42,
        "verbosity": 0
    }
    model = XGBClassifier(**params)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy', n_jobs=-1)
    return cv_scores.mean()

study = optuna.create_study(direction="maximize", study_name="xgboost_2025")
study.optimize(objective, n_trials=40, show_progress_bar=True, n_jobs=1)

print(f"\n✅ Best CV Accuracy: {study.best_value:.4f}")

# ---------------------------------------------------
# STEP 5: Train final model
# ---------------------------------------------------
print("\n🤖 Training final model...")
final_model = XGBClassifier(**study.best_params, eval_metric='logloss')
final_model.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=False)
print("✅ Model training complete!")

# ---------------------------------------------------
# STEP 6: Evaluate
# ---------------------------------------------------
print("\n📊 Evaluating model...")

# Cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(final_model, X_train, y_train, cv=cv, scoring='accuracy', n_jobs=-1)

# Test predictions
y_pred_test = final_model.predict(X_test)
y_pred_proba_test = final_model.predict_proba(X_test)[:, 1]
test_accuracy = accuracy_score(y_test, y_pred_test)

# Train predictions
y_pred_train = final_model.predict(X_train)
train_accuracy = accuracy_score(y_train, y_pred_train)

# Confusion matrix
cm = confusion_matrix(y_test, y_pred_test)

print(f"✅ Test Accuracy: {test_accuracy:.4f}")
print(f"✅ Train Accuracy: {train_accuracy:.4f}")

# ---------------------------------------------------
# STEP 7: Generate Detailed Reports
# ---------------------------------------------------
print("\n" + "="*70)
print(" 📝 GENERATING DETAILED REPORTS")
print("="*70)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ========================================================
# REPORT 1: Training Summary (JSON)
# ========================================================
training_summary = {
    "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "model_type": "XGBoost Classifier",
    "label_encoding": "0=Legitimate, 1=Phishing",
    "dataset": {
        "total_samples": len(X),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "num_features": len(X.columns),
        "label_distribution": label_distribution
    },
    "hyperparameters": study.best_params,
    "performance": {
        "test_accuracy": float(test_accuracy),
        "train_accuracy": float(train_accuracy),
        "cv_accuracy_mean": float(cv_scores.mean()),
        "cv_accuracy_std": float(cv_scores.std()),
        "overfitting_gap": float(train_accuracy - test_accuracy)
    },
    "confusion_matrix": {
        "true_negatives": int(cm[0][0]),
        "false_positives": int(cm[0][1]),
        "false_negatives": int(cm[1][0]),
        "true_positives": int(cm[1][1])
    }
}

json_path = "Models/2025/reports/training_summary_latest2025.json"
with open(json_path, 'w') as f:
    json.dump(training_summary, f, indent=4)
print(f"✅ Saved: training_summary_latest2025.json")

# ========================================================
# REPORT 2: Feature Importance (CSV & TXT)
# ========================================================
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': final_model.feature_importances_
}).sort_values('importance', ascending=False)

csv_path = "Models/2025/reports/feature_importance_latest2025.csv"
feature_importance.to_csv(csv_path, index=False)
print(f"✅ Saved: feature_importance_latest2025.csv")

# ========================================================
# REPORT 3: Human-Readable Report (TXT)
# ========================================================
report_lines = []
report_lines.append("="*80)
report_lines.append(" MODEL 2025 - TRAINING REPORT")
report_lines.append("="*80)
report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append(f"\n{'='*80}")
report_lines.append("\n📊 DATASET INFORMATION")
report_lines.append("-"*80)
report_lines.append(f"Total Samples:          {len(X):,}")
report_lines.append(f"Training Samples:       {len(X_train):,}")
report_lines.append(f"Test Samples:           {len(X_test):,}")
report_lines.append(f"Number of Features:     {len(X.columns)}")
report_lines.append(f"\nLabel Distribution:")
report_lines.append(f"  Legitimate:           {label_distribution.get('Legitimate', 0):,} ({label_distribution.get('Legitimate', 0)/len(y)*100:.1f}%)")
report_lines.append(f"  Phishing:             {label_distribution.get('Phishing', 0):,} ({label_distribution.get('Phishing', 0)/len(y)*100:.1f}%)")

report_lines.append(f"\n{'='*80}")
report_lines.append("\n🎯 MODEL PERFORMANCE")
report_lines.append("-"*80)
report_lines.append(f"Test Accuracy:          {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
report_lines.append(f"Train Accuracy:         {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
report_lines.append(f"CV Accuracy:            {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
report_lines.append(f"Overfitting Gap:        {train_accuracy - test_accuracy:.4f}")

if train_accuracy - test_accuracy < 0.02:
    report_lines.append("  ✅ Excellent - Minimal overfitting")
elif train_accuracy - test_accuracy < 0.05:
    report_lines.append("  ✅ Good - Slight overfitting (acceptable)")
else:
    report_lines.append("  ⚠️  Warning - Moderate to high overfitting detected")

report_lines.append(f"\n{'='*80}")
report_lines.append("\n📋 CONFUSION MATRIX")
report_lines.append("-"*80)
report_lines.append(f"True Negatives (Legit → Legit):      {cm[0][0]:,}")
report_lines.append(f"False Positives (Legit → Phishing):  {cm[0][1]:,}")
report_lines.append(f"False Negatives (Phishing → Legit):  {cm[1][0]:,}")
report_lines.append(f"True Positives (Phishing → Phishing): {cm[1][1]:,}")

# Calculate rates
fpr = cm[0][1] / (cm[0][0] + cm[0][1]) if (cm[0][0] + cm[0][1]) > 0 else 0
fnr = cm[1][0] / (cm[1][0] + cm[1][1]) if (cm[1][0] + cm[1][1]) > 0 else 0

report_lines.append(f"\nFalse Positive Rate:    {fpr:.4f} ({fpr*100:.2f}%)")
report_lines.append(f"False Negative Rate:    {fnr:.4f} ({fnr*100:.2f}%)")

report_lines.append(f"\n{'='*80}")
report_lines.append("\n🏆 TOP 20 MOST IMPORTANT FEATURES")
report_lines.append("-"*80)
for idx, row in feature_importance.head(20).iterrows():
    report_lines.append(f"{row['feature']:<30} {row['importance']:.6f}")

report_lines.append(f"\n{'='*80}")
report_lines.append("\n⚙️  HYPERPARAMETERS")
report_lines.append("-"*80)
for param, value in study.best_params.items():
    report_lines.append(f"{param:<25} {value}")

report_lines.append(f"\n{'='*80}")
report_lines.append("\n📌 LABEL ENCODING")
report_lines.append("-"*80)
report_lines.append("Class 0 = Legitimate (Safe websites)")
report_lines.append("Class 1 = Phishing (Malicious websites)")
report_lines.append("\nWhen predict_proba() returns [0.9, 0.1]:")
report_lines.append("  - 90% probability of Legitimate (index 0)")
report_lines.append("  - 10% probability of Phishing (index 1)")

report_lines.append(f"\n{'='*80}")
report_lines.append("\n✅ TRAINING COMPLETED SUCCESSFULLY")
report_lines.append("="*80)

txt_path = "Models/2025/reports/training_report_latest2025.txt"
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f"✅ Saved: training_report_latest2025.txt")

# ========================================================
# REPORT 4: Test Predictions Sample (CSV)
# ========================================================
test_results = pd.DataFrame({
    'actual_label': y_test,
    'predicted_label': y_pred_test,
    'prob_legitimate': 1 - y_pred_proba_test,
    'prob_phishing': y_pred_proba_test,
    'correct': y_test == y_pred_test
})

# Add human-readable labels
test_results['actual_class'] = test_results['actual_label'].map({0: 'Legitimate', 1: 'Phishing'})
test_results['predicted_class'] = test_results['predicted_label'].map({0: 'Legitimate', 1: 'Phishing'})

csv_path = "Models/2025/reports/test_predictions_latest2025.csv"
test_results.to_csv(csv_path, index=False)
print(f"✅ Saved: test_predictions_latest2025.csv")

# Show sample misclassifications
print("\n🔍 Sample Misclassifications:")
misclassified = test_results[~test_results['correct']].head(10)
if len(misclassified) > 0:
    print(misclassified[['actual_class', 'predicted_class', 'prob_phishing']].to_string(index=False))
else:
    print("   No misclassifications found!")

# ---------------------------------------------------
# STEP 8: Save model
# ---------------------------------------------------
print("\n💾 Saving model files...")
joblib.dump(final_model, "Models/2025/model_2025.pkl")
joblib.dump(list(X.columns), "Models/2025/features_2025.pkl")
joblib.dump(training_summary, "Models/2025/model_2025_metadata.pkl")

print("\n✅ All files saved:")
print("   - model_2025.pkl (model)")
print("   - features_2025.pkl (feature names)")
print("   - model_2025_metadata.pkl (metadata)")
print("   - reports/training_summary_latest2025.json")
print("   - reports/feature_importance_latest2025.csv")
print("   - reports/training_report_latest2025.txt")
print("   - reports/test_predictions_latest2025.csv")

print("\n" + "="*70)
print(" TRAINING COMPLETE!")
print("="*70)
print(f"\n📖 To view report: open Models/2025/reports/training_report_latest2025.txt")
print(f"📊 To analyze: open Models/2025/reports/*.csv in Excel")
print("\n" + "="*70)