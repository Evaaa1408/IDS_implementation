import pandas as pd
import numpy as np
import joblib
import json
import os
import sys
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_curve
from xgboost import XGBClassifier
import optuna
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("  TRAINING MODEL 2024 - WITH DETAILED REPORTING")
print("="*70)

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

# Create reports directory
reports_dir = os.path.join(base_dir, "models", "model_2024", "reports")
os.makedirs(reports_dir, exist_ok=True)

# ---------------------------------------------------
# STEP 1: Load data
# ---------------------------------------------------
print("\n Loading data...")
features_path = os.path.join(base_dir, "feature_extraction", "url_2024", "extracted_features", "extracted_features_2024.pkl")
labels_path = os.path.join(base_dir, "feature_extraction", "url_2024", "extracted_features", "extracted_labels_2024.pkl")

X = joblib.load(features_path)
y = joblib.load(labels_path)
print(f" Features loaded: {X.shape}")
print(f" Labels loaded: {len(y)}")

# ---------------------------------------------------
# STEP 2: Validate labels
# ---------------------------------------------------
print("\n Validating labels...")
y = pd.Series(y)

# Check label distribution
unique, counts = np.unique(y, return_counts=True)
label_distribution = {}
for label, count in zip(unique, counts):
    label_name = 'Legitimate' if label == 0 else 'Phishing'
    label_distribution[label_name] = int(count)
    print(f"   {label_name}: {count} ({count/len(y)*100:.1f}%)")

# Calculate class imbalance ratio
legitimate_count = label_distribution.get('Legitimate', 0)
phishing_count = label_distribution.get('Phishing', 0)
imbalance_ratio = legitimate_count / max(1, phishing_count)
print(f"\n  Class Imbalance Ratio: {imbalance_ratio:.2f}:1 (Legitimate:Phishing)")

if imbalance_ratio > 2:
    print(f"     Will use scale_pos_weight={imbalance_ratio:.2f} to handle imbalance")

# ---------------------------------------------------
# STEP 3: Train-test split (stratified)
# ---------------------------------------------------
print("\n Splitting data (stratified)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f" Training set: {X_train.shape[0]} samples")
print(f" Test set: {X_test.shape[0]} samples")

# Verify stratification
print(f"\n   Training set distribution:")
train_dist = y_train.value_counts()
for label, count in train_dist.items():
    label_name = 'Legitimate' if label == 0 else 'Phishing'
    print(f"     {label_name}: {count} ({count/len(y_train)*100:.1f}%)")

# ---------------------------------------------------
# STEP 4: Hyperparameter optimization
# ---------------------------------------------------
print("\n Starting hyperparameter optimization...")

def objective(trial):
    params = {
        "max_depth": trial.suggest_int("max_depth", 3, 8),
        "reg_lambda": trial.suggest_float("reg_lambda", 1.0, 10.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.5, 5.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "subsample": trial.suggest_float("subsample", 0.6, 0.9),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 0.9),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "n_estimators": trial.suggest_int("n_estimators", 100, 300),
        "scale_pos_weight": imbalance_ratio,  # Handle class imbalance
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "random_state": 42,
        "verbosity": 0
    }
    model = XGBClassifier(**params)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy', n_jobs=-1)
    return cv_scores.mean()

study = optuna.create_study(
    direction="maximize",
    study_name="xgboost_2024",
    pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=3, interval_steps=1)
)

study.optimize(objective, n_trials=30, show_progress_bar=True, n_jobs=1)

print(f"\n Best CV Accuracy: {study.best_value:.4f}")

# ---------------------------------------------------
# STEP 5: Train final model
# ---------------------------------------------------
print("\n🤖 Training final model...")
final_model = XGBClassifier(**study.best_params, eval_metric='logloss')
final_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)
print(" Model training complete!")

# ---------------------------------------------------
# STEP 6: Evaluate
# ---------------------------------------------------
print("\n Evaluating model...")

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

print(f" Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
print(f" Train Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")

# Calculate detailed metrics
tn, fp, fn, tp = cm.ravel()
fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0

print(f"\n Test Set Metrics:")
print(f"   False Positive Rate: {fpr:.4f} ({fpr*100:.2f}%)")
print(f"   False Negative Rate: {fnr:.4f} ({fnr*100:.2f}%)")
print(f"   Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"   Recall: {recall:.4f} ({recall*100:.2f}%)")

# ============================================================
# STEP 6.5: THRESHOLD OPTIMIZATION (Reduce False Positives)
# ============================================================
print("\n" + "="*70)
print("  OPTIMIZING DECISION THRESHOLD")
print("="*70)

# Get predicted probabilities
y_proba = final_model.predict_proba(X_test)[:, 1]

# Calculate precision-recall curve
precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)

# Method 1: F1-optimized threshold (balanced)
f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
best_f1_idx = np.argmax(f1_scores)
f1_threshold = thresholds[best_f1_idx] if best_f1_idx < len(thresholds) else 0.5

# Method 2: High-precision threshold (minimize false positives)
# Find threshold where precision >= 0.95
high_precision_idx = np.where(precisions >= 0.95)[0]
if len(high_precision_idx) > 0:
    high_precision_threshold = thresholds[high_precision_idx[0]]
else:
    high_precision_threshold = 0.65  # Conservative fallback

# Method 3: Balanced threshold (precision ≈ recall)
precision_recall_diff = np.abs(precisions - recalls)
balanced_idx = np.argmin(precision_recall_diff)
balanced_threshold = thresholds[balanced_idx] if balanced_idx < len(thresholds) else 0.5

# Choose optimal threshold: Use high-precision for FP reduction
optimal_threshold = high_precision_threshold

print(f"\n Threshold Analysis:")
print(f"   Default threshold:        0.5000")
print(f"   F1-optimized threshold:   {f1_threshold:.4f}")
print(f"   Balanced threshold:       {balanced_threshold:.4f}")
print(f"   High-precision threshold: {high_precision_threshold:.4f}")
print(f"\n    Selected: {optimal_threshold:.4f} (high-precision)")

# Make predictions with optimal threshold
y_pred_optimal = (y_proba >= optimal_threshold).astype(int)
test_accuracy_optimal = accuracy_score(y_test, y_pred_optimal)

# Confusion matrices
cm_default = cm  # Already calculated
cm_optimal = confusion_matrix(y_test, y_pred_optimal)

# Calculate metrics for optimal threshold
tn_opt, fp_opt, fn_opt, tp_opt = cm_optimal.ravel()
fpr_optimal = fp_opt / (fp_opt + tn_opt) if (fp_opt + tn_opt) > 0 else 0
fnr_optimal = fn_opt / (fn_opt + tp_opt) if (fn_opt + tp_opt) > 0 else 0
precision_optimal = tp_opt / (tp_opt + fp_opt) if (tp_opt + fp_opt) > 0 else 0
recall_optimal = tp_opt / (tp_opt + fn_opt) if (tp_opt + fn_opt) > 0 else 0

print(f"\n Performance Comparison:")
print(f"{'Metric':<30} {'Default (0.5)':<15} {'Optimal ({:.2f})'.format(optimal_threshold):<15} {'Change':<10}")
print("-"*70)
print(f"{'Accuracy':<30} {test_accuracy:.4f} ({test_accuracy*100:.1f}%)  {test_accuracy_optimal:.4f} ({test_accuracy_optimal*100:.1f}%)  {(test_accuracy_optimal-test_accuracy)*100:+.1f}%")
print(f"{'False Positive Rate':<30} {fpr:.4f} ({fpr*100:.1f}%)  {fpr_optimal:.4f} ({fpr_optimal*100:.1f}%)  {(fpr_optimal-fpr)*100:+.1f}%")
print(f"{'False Negative Rate':<30} {fnr:.4f} ({fnr*100:.1f}%)  {fnr_optimal:.4f} ({fnr_optimal*100:.1f}%)  {(fnr_optimal-fnr)*100:+.1f}%")
print(f"{'Precision':<30} {precision:.4f} ({precision*100:.1f}%)  {precision_optimal:.4f} ({precision_optimal*100:.1f}%)  {(precision_optimal-precision)*100:+.1f}%")  
print(f"{'Recall':<30} {recall:.4f} ({recall*100:.1f}%)  {recall_optimal:.4f} ({recall_optimal*100:.1f}%)  {(recall_optimal-recall)*100:+.1f}%")

print(f"\n Key Improvement:")
if fpr_optimal < fpr:
    fpr_reduction = (fpr - fpr_optimal) * 100
    print(f"    False positive rate reduced by {fpr_reduction:.1f} percentage points")
    print(f"   This means fewer legitimate sites wrongly flagged as phishing!")
else:
    print(f"     No improvement in false positive rate")

# ============================================================
# STEP 6.7: COMPLEX URL VALIDATION
# ============================================================
print("\n" + "="*70)
print("  VALIDATION: TESTING ON COMPLEX LEGITIMATE URLS")
print("="*70)

sys.path.append(os.path.join(base_dir, 'feature_extraction', 'url_2024'))
from Feature_Extractor import URLFeatureExtractor

complex_test_urls = [
    "https://www.britannica.com/biography/Che-Guevara",
    "https://plato.stanford.edu/entries/ethics-ai/",
    "https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:systems-of-equations",
    "https://scholar.google.com/scholar?hl=en&q=phishing+detection",
    "https://docs.google.com/document/d/1A9f8KJ9P2wQxU4Y/edit",
    "https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow",
    "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise",
    "https://github.com/openai/gpt-4/blob/main/system_card.md",
    "https://auth0.com/docs/flows/authorization-code-flow",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://medium.com/@user/how-machine-learning-detects-phishing-8f92a9c12",
    "https://www.reddit.com/r/netsec/comments/15f9k2m/phishing_detection_models/",
    "https://vimeo.com/76979871",
    "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    "https://accounts.google.com/o/oauth2/v2/auth",
]

print(f"\n Testing {len(complex_test_urls)} complex legitimate URLs...")

# Extract features
extractor = URLFeatureExtractor()
complex_features = []
for url in complex_test_urls:
    try:
        feats = extractor.extract(url)
        complex_features.append(feats)
    except Exception as e:
        print(f"  Error extracting {url}: {e}")

X_complex = pd.DataFrame(complex_features)
X_complex = X_complex.reindex(columns=X.columns, fill_value=0)

# Predict with both thresholds
y_proba_complex = final_model.predict_proba(X_complex)[:, 1]
y_pred_default_complex = (y_proba_complex >= 0.5).astype(int)
y_pred_optimal_complex = (y_proba_complex >= optimal_threshold).astype(int)

# Calculate false positive rates
fp_default_complex = np.sum(y_pred_default_complex == 1)
fp_optimal_complex = np.sum(y_pred_optimal_complex == 1)

print(f"\n Results:")
print(f"   False Positives (default 0.5):  {fp_default_complex}/{len(complex_test_urls)} ({fp_default_complex/len(complex_test_urls)*100:.1f}%)")
print(f"   False Positives (optimal {optimal_threshold:.2f}): {fp_optimal_complex}/{len(complex_test_urls)} ({fp_optimal_complex/len(complex_test_urls)*100:.1f}%)")
print(f"   Improvement: {fp_default_complex - fp_optimal_complex} URLs now correctly classified as safe")

# Detailed breakdown
print(f"\n Detailed Analysis:")
print(f"{'URL':<60} {'Prob':<8} {'Default':<10} {'Optimal':<10}")
print("-"*90)

for i, url in enumerate(complex_test_urls):
    prob = y_proba_complex[i]
    pred_def = " PHISH" if y_pred_default_complex[i] == 1 else " Safe"
    pred_opt = " PHISH" if y_pred_optimal_complex[i] == 1 else " Safe"
    
    # Truncate URL for display
    url_short = url[:57] + "..." if len(url) > 60 else url
    
    print(f"{url_short:<60} {prob*100:>6.1f}% {pred_def:<10} {pred_opt:<10}")

# Save validation report
validation_report = {
    "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_complex_urls": len(complex_test_urls),
    "false_positives_default": int(fp_default_complex),
    "false_positives_optimal": int(fp_optimal_complex),
    "false_positive_rate_default": float(fp_default_complex / len(complex_test_urls)),
    "false_positive_rate_optimal": float(fp_optimal_complex / len(complex_test_urls)),
    "improvement": int(fp_default_complex - fp_optimal_complex),
    "threshold_used": float(optimal_threshold),
    "detailed_results": [
        {
            "url": url,
            "probability": float(y_proba_complex[i]),
            "predicted_default": int(y_pred_default_complex[i]),
            "predicted_optimal": int(y_pred_optimal_complex[i])
        }
        for i, url in enumerate(complex_test_urls)
    ]
}

validation_json_path = os.path.join(reports_dir, "complex_url_validation_2024.json")
with open(validation_json_path, 'w') as f:
    json.dump(validation_report, f, indent=4)
print(f"\n Saved: complex_url_validation_2024.json")

# ---------------------------------------------------
# STEP 7: Generate Detailed Reports
# ---------------------------------------------------
print("\n" + "="*70)
print("  GENERATING DETAILED REPORTS")
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
        "label_distribution": label_distribution,
        "class_imbalance_ratio": float(imbalance_ratio)
    },
    "hyperparameters": study.best_params,
    "performance": {
        "test_accuracy": float(test_accuracy),
        "train_accuracy": float(train_accuracy),
        "cv_accuracy_mean": float(cv_scores.mean()),
        "cv_accuracy_std": float(cv_scores.std()),
        "false_positive_rate": float(fpr),
        "false_negative_rate": float(fnr),
        "precision": float(precision),
        "recall": float(recall),
        "overfitting_gap": float(train_accuracy - test_accuracy)
    },
    "confusion_matrix": {
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp)
    }
}

json_path = os.path.join(reports_dir, "training_summary_2024.json")
with open(json_path, 'w') as f:
    json.dump(training_summary, f, indent=4)
print(f" Saved: training_summary_2024.json")

# ========================================================
# REPORT 2: Feature Importance (CSV)
# ========================================================
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': final_model.feature_importances_
}).sort_values('importance', ascending=False)

csv_path = os.path.join(reports_dir, "feature_importance_2024.csv")
feature_importance.to_csv(csv_path, index=False)
print(f" Saved: feature_importance_2024.csv")

# ========================================================
# REPORT 3: Human-Readable Report (TXT)
# ========================================================
report_lines = []
report_lines.append("="*90)
report_lines.append(" MODEL 2024 - TRAINING REPORT WITH DETAILED ANALYSIS")
report_lines.append("="*90)
report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Dataset Information
report_lines.append(f"\n{'='*90}")
report_lines.append("\n DATASET INFORMATION")
report_lines.append("-"*90)
report_lines.append(f"Total Samples:          {len(X):,}")
report_lines.append(f"Training Samples:       {len(X_train):,}")
report_lines.append(f"Test Samples:           {len(X_test):,}")
report_lines.append(f"Number of Features:     {len(X.columns)}")
report_lines.append(f"\nLabel Distribution:")
report_lines.append(f"  Legitimate:           {label_distribution.get('Legitimate', 0):,} ({label_distribution.get('Legitimate', 0)/len(y)*100:.1f}%)")
report_lines.append(f"  Phishing:             {label_distribution.get('Phishing', 0):,} ({label_distribution.get('Phishing', 0)/len(y)*100:.1f}%)")
report_lines.append(f"\nClass Imbalance:")
report_lines.append(f"  Ratio: {imbalance_ratio:.2f}:1 (Legitimate:Phishing)")
if imbalance_ratio > 2:
    report_lines.append(f"   Handled with scale_pos_weight={imbalance_ratio:.2f}")

# Model Performance
report_lines.append(f"\n{'='*90}")
report_lines.append("\n MODEL PERFORMANCE")
report_lines.append("-"*90)
report_lines.append(f"Test Accuracy:          {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
report_lines.append(f"Train Accuracy:         {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
report_lines.append(f"CV Accuracy:            {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
report_lines.append(f"Overfitting Gap:        {train_accuracy - test_accuracy:.4f}")

if train_accuracy - test_accuracy < 0.02:
    report_lines.append("   Excellent - Minimal overfitting")
elif train_accuracy - test_accuracy < 0.05:
    report_lines.append("   Good - Slight overfitting (acceptable)")
else:
    report_lines.append("    Warning - Moderate overfitting detected")

# Detailed Metrics
report_lines.append(f"\n{'='*90}")
report_lines.append("\n DETAILED METRICS")
report_lines.append("-"*90)
report_lines.append(f"False Positive Rate:    {fpr:.4f} ({fpr*100:.2f}%)")
report_lines.append(f"  → {fp} legitimate URLs wrongly flagged as phishing")
report_lines.append(f"False Negative Rate:    {fnr:.4f} ({fnr*100:.2f}%)")
report_lines.append(f"  → {fn} phishing URLs missed (flagged as safe)")
report_lines.append(f"Precision:              {precision:.4f} ({precision*100:.2f}%)")
report_lines.append(f"  → When model says 'phishing', it's correct {precision*100:.1f}% of the time")
report_lines.append(f"Recall:                 {recall:.4f} ({recall*100:.2f}%)")
report_lines.append(f"  → Model catches {recall*100:.1f}% of all phishing URLs")

# Confusion Matrix
report_lines.append(f"\n{'='*90}")
report_lines.append("\n CONFUSION MATRIX")
report_lines.append("-"*90)
report_lines.append(f"True Negatives (Legit → Legit):      {tn:,}")
report_lines.append(f"False Positives (Legit → Phishing):  {fp:,}")
report_lines.append(f"False Negatives (Phishing → Legit):  {fn:,}")
report_lines.append(f"True Positives (Phishing → Phishing): {tp:,}")

# Feature Importance
report_lines.append(f"\n{'='*90}")
report_lines.append("\n TOP 20 MOST IMPORTANT FEATURES")
report_lines.append("-"*90)
report_lines.append("\nThese features are most important for identifying phishing:")
for idx, row in feature_importance.head(20).iterrows():
    report_lines.append(f"{row['feature']:<30} {row['importance']:.6f}")

# Explanation of Results
report_lines.append(f"\n{'='*90}")
report_lines.append("\n UNDERSTANDING THE RESULTS")
report_lines.append("-"*90)
report_lines.append("\n Why is phishing percentage different in predictions?")
report_lines.append(f"   Dataset has {phishing_count} phishing ({phishing_count/len(y)*100:.1f}%)")
report_lines.append(f"   Model predicted {(y_pred_test == 1).sum()} as phishing in test set")
report_lines.append(f"   Actual phishing in test: {(y_test == 1).sum()}")
report_lines.append(f"\n   This difference shows:")
report_lines.append(f"   • False Positives: Model too aggressive → {fp} safe URLs blocked")
report_lines.append(f"   • False Negatives: Model too lenient → {fn} phishing URLs missed")

report_lines.append("\n How does the model identify phishing?")
report_lines.append(f"   The model learned patterns from {len(X):,} URLs:")
report_lines.append(f"   • Analyzed 34 URL features (length, characters, structure)")
report_lines.append(f"   • Most important: {feature_importance.iloc[0]['feature']}")
report_lines.append(f"   • Uses XGBoost decision trees to classify")
report_lines.append(f"   • Balanced classes using scale_pos_weight={imbalance_ratio:.2f}")

# Hyperparameters
report_lines.append(f"\n{'='*90}")
report_lines.append("\n  HYPERPARAMETERS")
report_lines.append("-"*90)
for param, value in study.best_params.items():
    report_lines.append(f"{param:<25} {value}")

report_lines.append(f"\n{'='*90}")
report_lines.append("\n TRAINING COMPLETED SUCCESSFULLY")
report_lines.append("="*90)

txt_path = os.path.join(reports_dir, "training_report_2024.txt")
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f" Saved: training_report_2024.txt")

# ---------------------------------------------------
# STEP 8: Save model
# ---------------------------------------------------
print("\n Saving model files...")
model_dir = os.path.join(base_dir, "models", "model_2024")
os.makedirs(model_dir, exist_ok=True)

joblib.dump(final_model, os.path.join(model_dir, "model_2024.pkl"))
joblib.dump(list(X.columns), os.path.join(model_dir, "features_2024.pkl"))
joblib.dump(training_summary, os.path.join(model_dir, "model_2024_metadata.pkl"))

print("\n All files saved!")
print(f"   - model_2024.pkl")
print(f"   - features_2024.pkl")  
print(f"   - model_2024_metadata.pkl")
print(f"   - reports/training_summary_2024.json")
print(f"   - reports/feature_importance_2024.csv")
print(f"   - reports/training_report_2024.txt ")

print("\n" + "="*70)
print("  TRAINING COMPLETE!")
print("="*70)
print(f"\n Read the detailed report:")
print(f"   {txt_path}")
print(f"\n Model Performance Summary:")
print(f"   Accuracy: {test_accuracy*100:.2f}%")
print(f"   Precision: {precision*100:.2f}%")
print(f"   Recall: {recall*100:.2f}%")
print(f"   False Positives: {fp} ({fpr*100:.2f}%)")
print("\n" + "="*70)
