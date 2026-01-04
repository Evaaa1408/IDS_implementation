import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import os
import warnings

warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("  TRAINING MODEL 2023")
print("="*70)

# ---------------------------------------------------
# STEP 1: Load Data
# ---------------------------------------------------
dataset_path = "datasets/dataset_2023/Dataset2023.csv"
print(f"\n Loading dataset from {dataset_path}...")

try:
    df = pd.read_csv(dataset_path)
    print(f" Loaded {len(df)} samples")
except FileNotFoundError:
    print(" Dataset not found!")
    exit(1)

# ---------------------------------------------------
# STEP 2: Select Pure Content Features
# ---------------------------------------------------
print("\n Selecting Pure Content Features...")

content_features = [
    #28 features
    'LineOfCode', 'LargestLineLength', 'HasTitle', 'DomainTitleMatchScore', 
    'URLTitleMatchScore', 'HasFavicon', 'Robots', 'IsResponsive', 
    'NoOfURLRedirect', 'NoOfSelfRedirect', 'HasDescription', 'NoOfPopup', 
    'NoOfiFrame', 'HasExternalFormSubmit', 'HasSocialNet', 'HasSubmitButton', 
    'HasHiddenFields', 'HasPasswordField', 'Bank', 'Pay', 'Crypto', 
    'HasCopyrightInfo', 'NoOfImage', 'NoOfCSS', 'NoOfJS', 'NoOfSelfRef', 
    'NoOfEmptyRef', 'NoOfExternalRef',
]

missing = [c for c in content_features if c not in df.columns]
if missing:
    print(f" Missing columns in dataset: {missing}")
    exit(1)

X = df[content_features]
y = df['label']

print(f" Selected {len(content_features)} content features")

# ---------------------------------------------------
# STEP 3: Train/Test Split
# ---------------------------------------------------
print("\n Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Train: {len(X_train)}, Test: {len(X_test)}")

# ---------------------------------------------------
# STEP 4: Strong Random Forest
# ---------------------------------------------------
print("\n🤖 Training Random Forest Model 2023...")

rf = RandomForestClassifier(
    n_estimators=600,         
    max_depth=20,            
    min_samples_split=4,
    min_samples_leaf=2,
    max_features="sqrt",
    class_weight="balanced", 
    bootstrap=True,
    oob_score=True,         
    n_jobs=-1,
    random_state=42
)

rf.fit(X_train, y_train)

# ---------------------------------------------------
# STEP 5: Evaluation
# ---------------------------------------------------
print("\n Evaluating...")

train_pred = rf.predict(X_train)
test_pred = rf.predict(X_test)

train_acc = accuracy_score(y_train, train_pred)
test_acc = accuracy_score(y_test, test_pred)

print(f"   Train Accuracy: {train_acc:.4f}")
print(f"   Test Accuracy:  {test_acc:.4f}")
print(f"   OOB Score:      {rf.oob_score_:.4f}")
print(f"   Gap:            {train_acc - test_acc:.4f}")

print("\n Classification Report (Test):")
print(classification_report(y_test, test_pred, digits=4))

# ---------------------------------------------------
# META-FEATURE VISUALIZATION
# ---------------------------------------------------

print("\n" + "="*70)
print("  META-FEATURE ANALYSIS & VISUALIZATION")
print("="*70)

# Basic meta information
n_samples = len(X)
n_features = X.shape[1]
class_counts = pd.Series(y).value_counts().to_dict()

print(f"\n Dataset Meta Info:")
print(f"   Total samples:          {n_samples}")
print(f"   Number of features:     {n_features}")
print(f"   Legitimate samples:     {class_counts.get(0, 0)}")
print(f"   Phishing samples:       {class_counts.get(1, 0)}")

# Feature importance
print("\n Feature Importance (Top 20):")
importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": rf.feature_importances_
}).sort_values("importance", ascending=False)

print(importance_df.head(20).to_string(index=False))

# Summary statistics for features
print("\n Feature Summary Statistics:")
summary_stats = X.describe().T[["mean", "std", "min", "max"]]
print(summary_stats.head(15).to_string())

# ---------------------------------------------------
# SAVE METADATA
# ---------------------------------------------------
metadata = {
    "total_samples": n_samples,
    "num_features": n_features,
    "class_distribution": class_counts,
    "top_features": importance_df.head(20).to_dict(orient="records"),
    "feature_stats_head": summary_stats.head(15).to_dict(orient="index")
}

os.makedirs("Models/2023", exist_ok=True)
joblib.dump(metadata, "Models/2023/model_2023_metadata.pkl")

print("\n Metadata saved to: Models/2023/model_2023_metadata.pkl")
print("="*70)

# ---------------------------------------------------
# STEP 6: Save Model & Artifacts
# ---------------------------------------------------
print("\n Saving model...")
os.makedirs("Models/2023", exist_ok=True)

joblib.dump(rf, "Models/2023/model_2023.pkl")
joblib.dump(content_features, "Models/2023/features_2023.pkl")

print(" Model saved to Models/2023/model_2023.pkl")
print(" Features saved to Models/2023/features_2023.pkl")

# ---------------------------------------------------
# STEP 7: Generate Human-Readable Report
# ---------------------------------------------------
print("\n Generating human-readable report...")

report_path = "Models/2023/model_2023_report.txt"

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write("  MODEL 2023 TRAINING REPORT\n")
    f.write("="*70 + "\n\n")
    
    # Model Configuration
    f.write(" MODEL CONFIGURATION\n")
    f.write("-"*70 + "\n")
    f.write(f"Model Type:           Random Forest Classifier\n")
    f.write(f"Number of Trees:      {rf.n_estimators}\n")
    f.write(f"Max Depth:            {rf.max_depth}\n")
    f.write(f"Min Samples Split:    {rf.min_samples_split}\n")
    f.write(f"Min Samples Leaf:     {rf.min_samples_leaf}\n")
    f.write(f"Max Features:         {rf.max_features}\n")
    f.write(f"Class Weight:         {rf.class_weight}\n")
    f.write(f"Bootstrap:            {rf.bootstrap}\n")
    f.write(f"OOB Score Enabled:    {rf.oob_score}\n\n")
    
    # Dataset Information
    f.write("="*70 + "\n")
    f.write(" DATASET INFORMATION\n")
    f.write("="*70 + "\n")
    f.write(f"Total Samples:        {n_samples}\n")
    f.write(f"Number of Features:   {n_features}\n")
    f.write(f"Training Samples:     {len(X_train)}\n")
    f.write(f"Testing Samples:      {len(X_test)}\n\n")
    
    f.write("Class Distribution:\n")
    f.write(f"  Legitimate (0):     {class_counts.get(0, 0)} ({class_counts.get(0, 0)/n_samples*100:.2f}%)\n")
    f.write(f"  Phishing (1):       {class_counts.get(1, 0)} ({class_counts.get(1, 0)/n_samples*100:.2f}%)\n\n")
    
    # Performance Metrics
    f.write("="*70 + "\n")
    f.write(" MODEL PERFORMANCE\n")
    f.write("="*70 + "\n")
    f.write(f"Training Accuracy:    {train_acc:.4f} ({train_acc*100:.2f}%)\n")
    f.write(f"Testing Accuracy:     {test_acc:.4f} ({test_acc*100:.2f}%)\n")
    f.write(f"OOB Score:            {rf.oob_score_:.4f} ({rf.oob_score_*100:.2f}%)\n")
    f.write(f"Overfitting Gap:      {train_acc - test_acc:.4f}\n\n")
    
    # Detailed Classification Report
    f.write("="*70 + "\n")
    f.write(" DETAILED CLASSIFICATION REPORT (TEST SET)\n")
    f.write("="*70 + "\n")
    from sklearn.metrics import classification_report
    report_dict = classification_report(y_test, test_pred, output_dict=True)
    
    f.write("\nClass 0 (Legitimate):\n")
    f.write(f"  Precision:    {report_dict['0']['precision']:.4f}\n")
    f.write(f"  Recall:       {report_dict['0']['recall']:.4f}\n")
    f.write(f"  F1-Score:     {report_dict['0']['f1-score']:.4f}\n")
    f.write(f"  Support:      {int(report_dict['0']['support'])}\n\n")
    
    f.write("Class 1 (Phishing):\n")
    f.write(f"  Precision:    {report_dict['1']['precision']:.4f}\n")
    f.write(f"  Recall:       {report_dict['1']['recall']:.4f}\n")
    f.write(f"  F1-Score:     {report_dict['1']['f1-score']:.4f}\n")
    f.write(f"  Support:      {int(report_dict['1']['support'])}\n\n")
    
    # Confusion Matrix Analysis
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_test, test_pred)
    f.write("="*70 + "\n")
    f.write(" CONFUSION MATRIX ANALYSIS\n")
    f.write("="*70 + "\n")
    f.write(f"True Negatives (TN):   {cm[0][0]} (Correctly identified legitimate)\n")
    f.write(f"False Positives (FP):  {cm[0][1]} (Legitimate marked as phishing)\n")
    f.write(f"False Negatives (FN):  {cm[1][0]} (Phishing marked as legitimate)\n")
    f.write(f"True Positives (TP):   {cm[1][1]} (Correctly identified phishing)\n\n")
    
    # Error Analysis
    f.write(" ERROR ANALYSIS:\n")
    f.write(f"False Positive Rate:   {cm[0][1]/(cm[0][0]+cm[0][1])*100:.2f}%\n")
    f.write(f"False Negative Rate:   {cm[1][0]/(cm[1][0]+cm[1][1])*100:.2f}%\n\n")
    
    # Feature Importance
    f.write("="*70 + "\n")
    f.write(" FEATURE IMPORTANCE (ALL FEATURES)\n")
    f.write("="*70 + "\n")
    for idx, row in importance_df.iterrows():
        f.write(f"{row['feature']:35s} {row['importance']:.6f}\n")
    
    f.write("\n" + "="*70 + "\n")
    f.write(" FEATURE STATISTICS SUMMARY\n")
    f.write("="*70 + "\n\n")
    
    for feature in X.columns[:10]:  # First 10 features
        f.write(f"\n{feature}:\n")
        f.write(f"  Mean:     {X[feature].mean():.4f}\n")
        f.write(f"  Std Dev:  {X[feature].std():.4f}\n")
        f.write(f"  Min:      {X[feature].min():.4f}\n")
        f.write(f"  Max:      {X[feature].max():.4f}\n")
    
    # Model Interpretation
    f.write("\n" + "="*70 + "\n")
    f.write(" MODEL INTERPRETATION & INSIGHTS\n")
    f.write("="*70 + "\n\n")
    
    f.write("Top 5 Most Important Features:\n")
    for idx, row in importance_df.head(5).iterrows():
        f.write(f"  {idx+1}. {row['feature']} (importance: {row['importance']:.4f})\n")
    
    f.write("\n" + "="*70 + "\n")
    f.write("Report generated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    f.write("="*70 + "\n")

print(f" Human-readable report saved to: {report_path}")

# ---------------------------------------------------
# STEP 8: Print PKL File Contents for Verification
# ---------------------------------------------------
print("\n" + "="*70)
print("  VERIFYING SAVED PKL FILES")
print("="*70)

# Load and verify model PKL
print("\n Model PKL Contents:")
loaded_model = joblib.load("Models/2023/model_2023.pkl")
print(f"   Model Type: {type(loaded_model).__name__}")
print(f"   Number of Estimators: {loaded_model.n_estimators}")
print(f"   Max Depth: {loaded_model.max_depth}")
print(f"   Number of Features: {loaded_model.n_features_in_}")

# Load and verify features PKL
print("\n Features PKL Contents:")
loaded_features = joblib.load("Models/2023/features_2023.pkl")
print(f"   Number of Features: {len(loaded_features)}")
print(f"   Features List: {loaded_features[:5]}... (showing first 5)")

# Load and verify metadata PKL
print("\n Metadata PKL Contents:")
loaded_metadata = joblib.load("Models/2023/model_2023_metadata.pkl")
print(f"   Total Samples: {loaded_metadata['total_samples']}")
print(f"   Number of Features: {loaded_metadata['num_features']}")
print(f"   Class Distribution: {loaded_metadata['class_distribution']}")

print("\n All PKL files verified successfully!")
print("="*70 + "\n")