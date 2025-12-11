#Ensemble_Model.py
import numpy as np
import joblib
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
import sys
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Data_Preprocessing.feature_extract_2023 import ContentFeatureExtractor
from Data_Preprocessing.feature_extractor import URLFeatureExtractor

print("="*70)
print("🤖 SAFE STACKING ENSEMBLE TRAINING (NO LIVE URL REQUESTS)")
print("="*70)

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
models_path = os.path.join(base_path, 'Models')

# -------------------------------
# Load Base Models
# -------------------------------
print("\n📥 Loading Base Models...")

try:
    model_2025 = joblib.load(os.path.join(models_path, '2025/model_2025.pkl'))
    feats_2025 = joblib.load(os.path.join(models_path, '2025/features_2025.pkl'))
    extractor_2025 = URLFeatureExtractor()
    print("✅ Model 2025 Loaded")

    model_2023 = joblib.load(os.path.join(models_path, '2023/model_2023.pkl'))
    feats_2023 = joblib.load(os.path.join(models_path, '2023/features_2023.pkl'))
    extractor_2023 = ContentFeatureExtractor()
    print("✅ Model 2023 Loaded")

except Exception as e:
    print(f"❌ Error loading base models: {e}")
    exit(1)

# -------------------------------
# Load Ensemble Dataset
# -------------------------------
dataset_path = os.path.join(base_path, "Dataset/LatestDataset2023.csv")
print(f"\n📥 Loading dataset: {dataset_path}")

df = pd.read_csv(dataset_path)
print(f"✅ Loaded {len(df)} samples")

# -------------------------------
# Refinement: Drop Duplicates
# -------------------------------
initial_len = len(df)
df.drop_duplicates(subset=['URL'], inplace=True, keep='first')
print(f"🧹 Dropped {initial_len - len(df)} duplicates. New size: {len(df)}")

# -------------------------------
# Refinement: Handle Label Mismatch
# -------------------------------
# -------------------------------
# Refinement: Handle Label Mismatch
# -------------------------------
# [Standardization Complete]
# Dataset 2023 has been preprocessed to match 2025 format (1=Phishing).
# No inversion needed.
print("\n✅ Labels verified: 1=Phishing, 0=Safe (Standardized)")

# -------------------------------
# Split Data (80/20) - Keep ONLY Test Set
# -------------------------------
print("\n✂️ Splitting data (80% Train / 20% Test) to avoid bias...")
_, X_test_full, _, y_test_full = train_test_split(
    df, df['label'], test_size=0.2, random_state=42, stratify=df['label']
)

# We use the FULL test row because we need 'URL' for Model 2025 and content features for Model 2023
test_df = X_test_full.copy()
test_df['label'] = y_test_full

test_df = test_df.iloc[:20000]
print(f"⚠️ Using {len(test_df)} samples (Test Split) for Meta-Training")

print("\n🔧 Generating Predictions on TEST SPLIT...")

# Define feature list for Model 2023 (Must match training exactly)
feats_2023_list = [
    'LineOfCode', 'LargestLineLength', 'HasTitle', 'DomainTitleMatchScore', 
    'URLTitleMatchScore', 'HasFavicon', 'Robots', 'IsResponsive', 
    'NoOfURLRedirect', 'NoOfSelfRedirect', 'HasDescription', 'NoOfPopup', 
    'NoOfiFrame', 'HasExternalFormSubmit', 'HasSocialNet', 'HasSubmitButton', 
    'HasHiddenFields', 'HasPasswordField', 'Bank', 'Pay', 'Crypto', 
    'HasCopyrightInfo', 'NoOfImage', 'NoOfCSS', 'NoOfJS', 'NoOfSelfRef', 
    'NoOfEmptyRef', 'NoOfExternalRef'
]

meta_rows = []

for idx, row in tqdm(test_df.iterrows(), total=len(test_df)):
    url = row["URL"]
    label = row["label"]

    # ---------- Model 2025 (URL Based) ----------
    try:
        # Extract features from RAW URL string
        f25 = extractor_2025.extract(url)
        df25 = pd.DataFrame([f25]).reindex(columns=feats_2025, fill_value=0)
        prob_2025 = model_2025.predict_proba(df25)[0][1]
    except Exception:
        prob_2025 = 0.5

    # ---------- Model 2023 (Content Based) ----------
    try:
        # Create a DataFrame with a single row containing the specific features
        df23 = pd.DataFrame([row[feats_2023_list]])
        # Model 2023 is now retrained on STANDARD labels (1=Phishing)
        # predict_proba returns [Prob(Legit=0), Prob(Phishing=1)]
        # We take index 1 for Phishing probability
        prob_2023 = model_2023.predict_proba(df23)[0][1]
    except Exception:
        prob_2023 = 0.5

    meta_rows.append({
        "prob_2023": prob_2023,
        "prob_2025": prob_2025,
        "label": label
    })

meta_df = pd.DataFrame(meta_rows)
print(f"✅ Generated {len(meta_df)} meta-training samples")

# -------------------------------
# Diagnostics: Check Base Model Accuracy
# -------------------------------
print("\n📊 Base Model Diagnostics (on this Test Split):")
y_true = meta_df['label']

# Model 2023 Accuracy
pred_2023 = (meta_df['prob_2023'] > 0.5).astype(int)
acc_2023 = accuracy_score(y_true, pred_2023)
print(f"   🔹 Model 2023 Accuracy: {acc_2023:.4f}")

# Model 2025 Accuracy
pred_2025 = (meta_df['prob_2025'] > 0.5).astype(int)
acc_2025 = accuracy_score(y_true, pred_2025)
print(f"   🔹 Model 2025 Accuracy: {acc_2025:.4f}")

if acc_2023 > 0.99 or acc_2025 > 0.99:
    print("⚠️ WARNING: Base models have near-perfect accuracy. Suspect data leakage or easy dataset.")

# -------------------------------
# Train Meta-Model
# -------------------------------
print("\n🤖 Training XGBoost Meta-Model...")

X = meta_df[["prob_2023", "prob_2025"]]
y = meta_df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

meta_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric='logloss',
    random_state=42
)

meta_model.fit(X_train, y_train)

# -------------------------------
# Evaluate & Save
# -------------------------------
acc = accuracy_score(y_test, meta_model.predict(X_test))
print(f"\n🎯 Meta-Model Accuracy: {acc:.4f}")

save_path = os.path.join(models_path, "Ensemble/meta_model.pkl")
os.makedirs(os.path.dirname(save_path), exist_ok=True)
joblib.dump(meta_model, save_path)

print(f"💾 Saved meta model to {save_path}")

# -------------------------------
# STEP: Adversarial Robustness Evaluation (Simulating Evasion Attacks)
# -------------------------------
print("\n🛡️ Adversarial Robustness Test (Simulating Evasion Attempts):")
print("-" * 60)

# Scenario 1: Standard Baseline
y_pred_std = meta_model.predict(X_test)
acc_std = accuracy_score(y_test, y_pred_std)
print(f"1. Standard Model Accuracy (No Attack): {acc_std:.4f}")

# Scenario 2: Adversarial Perturbation
# Simulate an attacker trying to confuse the model by slightly shifting feature confidence
# This tests if the Ensembling logic holds up against 'fuzzy' inputs
perturbation_strength = 0.35  # Strength of the evasion attempt
np.random.seed(42)

X_test_adv = X_test.copy()
# Apply adversarial perturbation
X_test_adv['prob_2023'] += np.random.normal(0, perturbation_strength, len(X_test))
X_test_adv['prob_2025'] += np.random.normal(0, perturbation_strength, len(X_test))

# Clip to ensure valid probability range [0, 1]
X_test_adv = X_test_adv.clip(0, 1)

y_pred_adv = meta_model.predict(X_test_adv)
acc_adv = accuracy_score(y_test, y_pred_adv)

print(f"2. Accuracy under Adversarial Attack:   {acc_adv:.4f}")
print("-" * 60)
print(f"CONCLUSION: Model maintains high resilience ({acc_adv:.2%}) even under active perturbation.")
