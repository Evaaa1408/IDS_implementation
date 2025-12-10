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
print(" 🚀 TRAINING MODEL 2023")
print("="*70)

# ---------------------------------------------------
# STEP 1: Load Data
# ---------------------------------------------------
dataset_path = "Dataset/LatestDataset2023.csv"
print(f"\n📥 Loading dataset from {dataset_path}...")

try:
    df = pd.read_csv(dataset_path)
    print(f"✅ Loaded {len(df)} samples")
except FileNotFoundError:
    print("❌ Dataset not found!")
    exit(1)

# ---------------------------------------------------
# STEP 2: Select Pure Content Features
# ---------------------------------------------------
print("\n🔧 Selecting Pure Content Features...")

content_features = [
    'LineOfCode', 'LargestLineLength', 'HasTitle', 'DomainTitleMatchScore', 
    'URLTitleMatchScore', 'HasFavicon', 'Robots', 'IsResponsive', 
    'NoOfURLRedirect', 'NoOfSelfRedirect', 'HasDescription', 'NoOfPopup', 
    'NoOfiFrame', 'HasExternalFormSubmit', 'HasSocialNet', 'HasSubmitButton', 
    'HasHiddenFields', 'HasPasswordField', 'Bank', 'Pay', 'Crypto', 
    'HasCopyrightInfo', 'NoOfImage', 'NoOfCSS', 'NoOfJS', 'NoOfSelfRef', 
    'NoOfEmptyRef', 'NoOfExternalRef'
]

missing = [c for c in content_features if c not in df.columns]
if missing:
    print(f"❌ Missing columns in dataset: {missing}")
    exit(1)

X = df[content_features]
y = df['label']

print(f"✅ Selected {len(content_features)} content features")

# ---------------------------------------------------
# STEP 3: Train/Test Split
# ---------------------------------------------------
print("\n📊 Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Train: {len(X_train)}, Test: {len(X_test)}")

# ---------------------------------------------------
# STEP 4: Strong Random Forest (Enhanced)
# ---------------------------------------------------
print("\n🤖 Training Enhanced Random Forest Model 2023...")

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
print("\n🔍 Evaluating...")

train_pred = rf.predict(X_train)
test_pred = rf.predict(X_test)

train_acc = accuracy_score(y_train, train_pred)
test_acc = accuracy_score(y_test, test_pred)

print(f"   Train Accuracy: {train_acc:.4f}")
print(f"   Test Accuracy:  {test_acc:.4f}")
print(f"   OOB Score:      {rf.oob_score_:.4f}")
print(f"   Gap:            {train_acc - test_acc:.4f}")

print("\n📊 Classification Report (Test):")
print(classification_report(y_test, test_pred, digits=4))

# ---------------------------------------------------
# META-FEATURE VISUALIZATION (No CSV file created)
# ---------------------------------------------------

print("\n" + "="*70)
print(" 📊 META-FEATURE ANALYSIS & VISUALIZATION")
print("="*70)

# Basic meta information
n_samples = len(X)
n_features = X.shape[1]
class_counts = pd.Series(y).value_counts().to_dict()

print(f"\n📈 Dataset Meta Info:")
print(f"   Total samples:          {n_samples}")
print(f"   Number of features:     {n_features}")
print(f"   Legitimate samples:     {class_counts.get(0, 0)}")
print(f"   Phishing samples:       {class_counts.get(1, 0)}")

# Feature importance
print("\n🏆 Feature Importance (Top 20):")
importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": rf.feature_importances_
}).sort_values("importance", ascending=False)

print(importance_df.head(20).to_string(index=False))

# Summary statistics for features
print("\n📊 Feature Summary Statistics:")
summary_stats = X.describe().T[["mean", "std", "min", "max"]]
print(summary_stats.head(15).to_string())

# ---------------------------------------------------
# SAVE METADATA (No CSV file)
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

print("\n💾 Metadata saved to: Models/2023/model_2023_metadata.pkl")
print("="*70)

# ---------------------------------------------------
# STEP 6: Save Model & Artifacts
# ---------------------------------------------------
print("\n💾 Saving model...")
os.makedirs("Models/2023", exist_ok=True)

joblib.dump(rf, "Models/2023/model_2023.pkl")
joblib.dump(content_features, "Models/2023/features_2023.pkl")

print("✅ Model saved to Models/2023/model_2023.pkl")
print("✅ Features saved to Models/2023/features_2023.pkl")
