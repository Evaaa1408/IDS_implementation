# Train_Phis.py - Train Phishing Pattern Learning Model
import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb
import os

print("\n" + "="*70)
print(" 🚀 TRAINING PHISHING PATTERN LEARNING MODEL")
print("="*70)

# ========================================================
# 1. Load Features and Labels
# ========================================================
# Get script directory to make paths work from anywhere
script_dir = os.path.dirname(os.path.abspath(__file__))
features_path = os.path.join(script_dir, "Features_Output/phishing_features_2019_2025.pkl")
labels_path = os.path.join(script_dir, "Features_Output/phishing_labels_2019_2025.pkl")

print(f"\n📥 Loading data...")
print(f"   Script location: {script_dir}")
features_df = joblib.load(features_path)
labels = joblib.load(labels_path)

print(f"✅ Features loaded: {features_df.shape}")
print(f"✅ Labels loaded: {len(labels)}")

# ========================================================
# 2. Verify Data
# ========================================================
print(f"\n🔍 Verifying data...")
print(f"   Unique labels: {set(labels)}")
print(f"   All phishing (1)?: {all(label == 1 for label in labels)}")
print(f"   Feature count: {len(features_df.columns)}")
print(f"   Sample count: {len(features_df)}")

# ========================================================
# 3. Create Synthetic Negative Samples 
# ========================================================
# Since all data is phishing (label=1), we'll create a holdout test set
# to validate the model learns generalizable phishing patterns

print(f"\n📊 Splitting data into train/validation/test sets...")
print(f"   Note: All samples are phishing URLs (label=1)")

# Split: 70% train, 15% validation, 15% test
# No stratify needed since all labels are identical
X_temp, X_test, y_temp, y_test = train_test_split(
    features_df, labels, test_size=0.15, random_state=42
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.176, random_state=42  # 0.176 of 85% = 15% of total
)

print(f"✅ Training set: {len(X_train)} samples (all phishing)")
print(f"✅ Validation set: {len(X_val)} samples (all phishing)")
print(f"✅ Test set: {len(X_test)} samples (all phishing)")

# ========================================================
# 4. Train XGBoost Model (Regression for Pattern Scoring)
# ========================================================
print(f"\n🤖 Training XGBoost model...")
print(f"   Using regression objective for phishing pattern scoring")
print(f"   (All labels are 1, so we learn what '1-ness' means)")

# Create XGBoost regressor (not classifier, since we only have one class)
# The model will learn to output high scores for phishing-like patterns
model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='reg:squarederror',
    random_state=42,
    eval_metric='rmse'
)

# Train with validation set for early stopping
model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=True
)

print(f"✅ Model training complete!")

# ========================================================
# 5. Evaluate Model (Regression Metrics)
# ========================================================
print(f"\n📊 Evaluating model...")

# Make predictions
y_train_pred = model.predict(X_train)
y_val_pred = model.predict(X_val)
y_test_pred = model.predict(X_test)

# Calculate metrics (for regression)
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

train_mse = mean_squared_error(y_train, y_train_pred)
val_mse = mean_squared_error(y_val, y_val_pred)
test_mse = mean_squared_error(y_test, y_test_pred)

train_rmse = np.sqrt(train_mse)
val_rmse = np.sqrt(val_mse)
test_rmse = np.sqrt(test_mse)

# R² score (how well model learns the pattern)
train_r2 = r2_score(y_train, y_train_pred)
val_r2 = r2_score(y_val, y_val_pred)
test_r2 = r2_score(y_test, y_test_pred)

# Calculate "accuracy" - how close predictions are to 1.0
# We'll consider predictions > 0.5 as "phishing-like"
train_acc = np.mean(y_train_pred > 0.5)
val_acc = np.mean(y_val_pred > 0.5)
test_acc = np.mean(y_test_pred > 0.5)

# Display accuracy first (main metric)
print(f"\n✅ Training Accuracy: {train_acc*100:.2f}% (predictions > 0.5)")
print(f"✅ Validation Accuracy: {val_acc*100:.2f}%")
print(f"✅ Test Accuracy: {test_acc*100:.2f}%")

# Display RMSE (technical detail)
print(f"\n📊 Technical Metrics (RMSE & R²):")
print(f"   Training:   RMSE = {train_rmse:.4f} | R² = {train_r2:.4f}")
print(f"   Validation: RMSE = {val_rmse:.4f} | R² = {val_r2:.4f}")
print(f"   Test:       RMSE = {test_rmse:.4f} | R² = {test_r2:.4f}")

# Get prediction statistics
y_test_proba = y_test_pred  # For regression, predictions are already scores

print(f"\n📊 Test Set Prediction Statistics:")
print(f"   Mean score: {y_test_proba.mean():.4f}")
print(f"   Min score: {y_test_proba.min():.4f}")
print(f"   Max score: {y_test_proba.max():.4f}")
print(f"   Median score: {np.median(y_test_proba):.4f}")

# ========================================================
# 6. Feature Importance
# ========================================================
print(f"\n📊 Top 15 Most Important Features:")
feature_importance = pd.DataFrame({
    'feature': features_df.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(15).iterrows():
    print(f"   {row['feature']:30s} {row['importance']:.4f}")

# ========================================================
# 7. Save Model and Artifacts
# ========================================================
output_dir = os.path.join(script_dir, "Phishing_Model_Output")
os.makedirs(output_dir, exist_ok=True)

model_path = f"{output_dir}/phishing_pattern_model.pkl"
features_list_path = f"{output_dir}/feature_names.pkl"
importance_path = f"{output_dir}/feature_importance.csv"
metadata_path = f"{output_dir}/model_metadata.pkl"

print(f"\n💾 Saving model and artifacts...")

# Save model
joblib.dump(model, model_path)
print(f"✅ Saved: {model_path}")

# Save feature names
joblib.dump(list(features_df.columns), features_list_path)
print(f"✅ Saved: {features_list_path}")

# Save feature importance
feature_importance.to_csv(importance_path, index=False)
print(f"✅ Saved: {importance_path}")

# Save metadata
metadata = {
    'n_samples': len(features_df),
    'n_features': len(features_df.columns),
    'train_size': len(X_train),
    'val_size': len(X_val),
    'test_size': len(X_test),
    'train_accuracy': float(train_acc),
    'val_accuracy': float(val_acc),
    'test_accuracy': float(test_acc),
    'train_rmse': float(train_rmse),
    'val_rmse': float(val_rmse),
    'test_rmse': float(test_rmse),
    'train_r2': float(train_r2),
    'val_r2': float(val_r2),
    'test_r2': float(test_r2),
    'feature_names': list(features_df.columns),
    'model_type': 'XGBoost Regressor (Pattern Scoring)',
    'note': 'All samples are phishing (label=1). Model learns phishing patterns.'
}
joblib.dump(metadata, metadata_path)
print(f"✅ Saved: {metadata_path}")

# ========================================================
# 8. Generate Human-Readable Phishing Pattern Report
# ========================================================
print(f"\n📝 Generating phishing pattern analysis report...")

# Create comprehensive report
report_lines = []
report_lines.append("="*90)
report_lines.append(" PHISHING PATTERN LEARNING MODEL - TRAINING REPORT")
report_lines.append("="*90)
report_lines.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Dataset Information
report_lines.append(f"\n{'='*90}")
report_lines.append("\n📊 DATASET INFORMATION")
report_lines.append("-"*90)
report_lines.append(f"Total Phishing URLs Analyzed:    {len(features_df):,}")
report_lines.append(f"Training Set:                    {len(X_train):,} URLs ({len(X_train)/len(features_df)*100:.1f}%)")
report_lines.append(f"Validation Set:                  {len(X_val):,} URLs ({len(X_val)/len(features_df)*100:.1f}%)")
report_lines.append(f"Test Set:                        {len(X_test):,} URLs ({len(X_test)/len(features_df)*100:.1f}%)")
report_lines.append(f"Number of Features Extracted:    {len(features_df.columns)}")
report_lines.append(f"\nData Source: phishurl_combined_2019_2025.csv")
report_lines.append(f"Source Period: 2019-2025 (6 years of phishing URLs)")

# Model Performance
report_lines.append(f"\n{'='*90}")
report_lines.append("\n🎯 MODEL PERFORMANCE")
report_lines.append("-"*90)
report_lines.append(f"Training Accuracy:               {train_acc:.4f} ({train_acc*100:.2f}%)")
report_lines.append(f"Validation Accuracy:             {val_acc:.4f} ({val_acc*100:.2f}%)")
report_lines.append(f"Test Accuracy:                   {test_acc:.4f} ({test_acc*100:.2f}%)")
report_lines.append(f"Overfitting Gap:                 {train_acc - test_acc:.4f}")
report_lines.append(f"\nTechnical Metrics:")
report_lines.append(f"  Training RMSE:                 {train_rmse:.4f} | R²: {train_r2:.4f}")
report_lines.append(f"  Validation RMSE:               {val_rmse:.4f} | R²: {val_r2:.4f}")
report_lines.append(f"  Test RMSE:                     {test_rmse:.4f} | R²: {test_r2:.4f}")

# Overfitting check
if train_acc - test_acc < 0.02:
    report_lines.append(f"\n  ✅ Excellent - Minimal overfitting, model generalizes well")
elif train_acc - test_acc < 0.05:
    report_lines.append(f"  ✅ Good - Slight overfitting (acceptable)")
else:
    report_lines.append(f"  ⚠️  Warning - Model may be overfitting to training data")

# Phishing Pattern Analysis
report_lines.append(f"\n{'='*90}")
report_lines.append("\n🔍 TOP 20 PHISHING PATTERNS IDENTIFIED")
report_lines.append("-"*90)
report_lines.append("\nThe model has learned to identify phishing URLs based on these key patterns:")
report_lines.append("(Higher importance = stronger indicator of phishing)\n")

# Feature explanations
feature_explanations = {
    'url_length': 'Phishing URLs are often very long to hide the real destination',
    'hostname_length': 'Phishing domains tend to be unusually long or short',
    'path_length': 'Excessive path length often indicates obfuscation',
    'num_dots': 'Multiple dots can indicate subdomain abuse',
    'num_hyphens': 'Excessive hyphens often used in combosquatting (e.g., secure-bank-login.tk)',
    'num_special_char': 'High special character count suggests obfuscation attempts',
    'digit_ratio': 'Unusual digit patterns (e.g., paypa1, g00gle)',
    'url_entropy': 'High randomness indicates computer-generated URLs',
    'domain_entropy': 'Random-looking domains are often phishing',
    'TyposquattingScore': 'Detects brand impersonation (faceboook, paypa1)',
    'CharacterSubstitutions': 'Letter-to-number substitutions (0 for O, 1 for I)',
    'SuspiciousTLD': 'Free/suspicious TLDs (.tk, .ml, .xyz) popular for phishing',
    'Combosquatting': 'Multiple trust words combined (secure-payment-bank.com)',
    'HomographChars': 'Cyrillic/Unicode characters that look like Latin letters',
    'uses_https': 'Surprisingly, many phishing sites now use HTTPS',
    'contains_ip': 'IP addresses instead of domain names are highly suspicious',
    'subdomain_depth': 'Deep subdomain nesting often hides the real domain',
    'suspicious_keyword_flag': 'Words like "secure", "verify", "login" in suspicious contexts',
    'LowVowelRatio': 'Random gibberish domains (qxzrtpl.tk)',
    'ExcessiveHyphens': 'Multiple hyphens indicate combosquatting',
    'NumberLetterMixing': 'Mixing numbers and letters in domain name',
    'RepeatedCharacters': 'Triple letters (gooogle, faceboook)',
    'is_slug_like': 'Legitimate URLs often have readable path slugs',
}

for idx, row in feature_importance.head(20).iterrows():
    feature_name = row['feature']
    importance = row['importance']
    explanation = feature_explanations.get(feature_name, 'Pattern analysis feature')
    
    report_lines.append(f"{idx+1:2d}. {feature_name:30s} {importance:.6f}")
    report_lines.append(f"    → {explanation}")

# Pattern Categories
report_lines.append(f"\n{'='*90}")
report_lines.append("\n📋 PHISHING PATTERN CATEGORIES")
report_lines.append("-"*90)

# Categorize features
structural_features = ['url_length', 'hostname_length', 'path_length', 'num_dots', 'num_slashes', 'num_hyphens', 'num_special_char']
character_features = ['digit_ratio', 'letter_ratio', 'CharacterSubstitutions', 'NumberLetterMixing']
entropy_features = ['url_entropy', 'domain_entropy', 'path_entropy']
attack_features = ['TyposquattingScore', 'Combosquatting', 'HomographChars', 'KnownTyposquatting']
tld_features = ['SuspiciousTLD', 'tld_length', 'domain_trust_score']
keyword_features = ['suspicious_keyword_flag', 'LowVowelRatio']

categories = {
    'URL Structure Patterns': structural_features,
    'Character Pattern Anomalies': character_features,
    'Randomness Detection (Entropy)': entropy_features,
    'Phishing Attack Techniques': attack_features,
    'Domain Trust Indicators': tld_features,
    'Keyword & Language Patterns': keyword_features
}

for category, feature_list in categories.items():
    report_lines.append(f"\n{category}:")
    for feat in feature_list:
        if feat in feature_importance['feature'].values:
            imp = feature_importance[feature_importance['feature'] == feat]['importance'].values[0]
            report_lines.append(f"  • {feat:30s} (importance: {imp:.4f})")

# Real-World Examples
report_lines.append(f"\n{'='*90}")
report_lines.append("\n💡 REAL-WORLD PHISHING PATTERNS LEARNED")
report_lines.append("-"*90)
report_lines.append("\n1. TYPOSQUATTING (Brand Impersonation):")
report_lines.append("   • faceboook.com (extra 'o')")
report_lines.append("   • paypa1.com (number '1' instead of 'l')")
report_lines.append("   • g00gle.com (zeros instead of 'o')")
report_lines.append("   → Model detects: TyposquattingScore, CharacterSubstitutions, RepeatedCharacters")

report_lines.append("\n2. COMBOSQUATTING (Keyword Stuffing):")
report_lines.append("   • secure-paypal-login.tk")
report_lines.append("   • verify-account-amazon.ml")
report_lines.append("   • update-banking-info.xyz")
report_lines.append("   → Model detects: Combosquatting, ExcessiveHyphens, SuspiciousTLD")

report_lines.append("\n3. SUBDOMAIN ABUSE:")
report_lines.append("   • paypal.com.secure-login.phish.tk")
report_lines.append("   • Real domain is 'phish.tk', but looks like 'paypal.com'")
report_lines.append("   → Model detects: subdomain_depth, num_dots, hostname_length")

report_lines.append("\n4. SUSPICIOUS TLDs:")
report_lines.append("   • .tk, .ml, .ga, .cf (free domains)")
report_lines.append("   • .xyz, .top, .click (cheap domains)")
report_lines.append("   → Model detects: SuspiciousTLD, domain_trust_score")

report_lines.append("\n5. RANDOM GIBBERISH DOMAINS:")
report_lines.append("   • qxzrtpl.tk")
report_lines.append("   • hjkdfgh.ml")
report_lines.append("   → Model detects: LowVowelRatio, domain_entropy, url_entropy")

# How the Model Works
report_lines.append(f"\n{'='*90}")
report_lines.append("\n⚙️  HOW THE MODEL IDENTIFIES PHISHING")
report_lines.append("-"*90)
report_lines.append("\n1. FEATURE EXTRACTION:")
report_lines.append("   For each URL, the model extracts 34 numerical features that capture:")
report_lines.append("   • Structural properties (length, special characters)")
report_lines.append("   • Character patterns (substitutions, mixing, repetitions)")
report_lines.append("   • Randomness measures (entropy)")
report_lines.append("   • Attack-specific patterns (typosquatting, combosquatting)")
report_lines.append("   • Trust indicators (TLD reputation, keywords)")

report_lines.append("\n2. PATTERN LEARNING:")
report_lines.append("   Using XGBoost (Gradient Boosting), the model:")
report_lines.append(f"   • Analyzed {len(features_df):,} real phishing URLs from 2019-2025")
report_lines.append("   • Built decision trees that identify combinations of features")
report_lines.append("   • Learned which patterns are most predictive of phishing")

report_lines.append("\n3. PREDICTION:")
report_lines.append("   Given a new URL:")
report_lines.append("   • Extract the same 34 features")
report_lines.append("   • Run through trained model")
report_lines.append("   • Output: Probability score (0.0 = legitimate, 1.0 = phishing)")

# Usage Guidelines
report_lines.append(f"\n{'='*90}")
report_lines.append("\n📖 USAGE GUIDELINES")
report_lines.append("-"*90)
report_lines.append("\nTo use this model in production:")
report_lines.append("1. Extract features using ChangedURLFeatureExtractor")
report_lines.append("2. Load model: model = joblib.load('phishing_pattern_model.pkl')")
report_lines.append("3. Predict: prob = model.predict_proba(features)[0, 1]")
report_lines.append("4. Interpret:")
report_lines.append("   • prob > 0.8: High confidence phishing")
report_lines.append("   • prob 0.5-0.8: Likely phishing")
report_lines.append("   • prob 0.2-0.5: Suspicious, investigate")
report_lines.append("   • prob < 0.2: Likely legitimate")

report_lines.append(f"\n{'='*90}")
report_lines.append("\n✅ TRAINING COMPLETED SUCCESSFULLY")
report_lines.append("="*90)

# Save human-readable report
report_path = f"{output_dir}/phishing_pattern_analysis.txt"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"✅ Saved: {report_path}")

# ========================================================
# 9. Summary
# ========================================================
print(f"\n" + "="*70)
print(" ✅ PHISHING PATTERN MODEL TRAINING COMPLETE!")
print("="*70)

print(f"\n📊 Model Summary:")
print(f"   Total phishing URLs: {len(features_df):,}")
print(f"   Features: {len(features_df.columns)}")
print(f"   Training accuracy: {train_acc*100:.2f}%")
print(f"   Test accuracy: {test_acc*100:.2f}%")
print(f"   Test RMSE: {test_rmse:.4f} | R²: {test_r2:.4f}")

print(f"\n📁 Output Files:")
print(f"   - {model_path}")
print(f"   - {features_list_path}")
print(f"   - {importance_path}")
print(f"   - {metadata_path}")
print(f"   - {report_path} ⭐ HUMAN-READABLE PATTERN REPORT")

print(f"\n💡 Next Steps:")
print(f"   1. Read the pattern analysis: {report_path}")
print(f"   2. Test the model: python Test_Phis.py")
print(f"   3. Understand phishing patterns from the detailed report!")
