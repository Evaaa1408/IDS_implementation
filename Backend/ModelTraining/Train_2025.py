#Train_2025.py
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
import optuna
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print(" 🚀 TRAINING MODEL 2025 - XGBoost Classifier")
print("="*70)

# ---------------------------------------------------
# STEP 1: Load extracted features and labels
# ---------------------------------------------------
print("\n📥 Loading data...")

X = joblib.load("features_2025.pkl")
y = joblib.load("labels_2025.pkl")

print(f"✅ Features loaded: {X.shape}")
print(f"✅ Labels loaded: {len(y)}")

# ---------------------------------------------------
# STEP 2: Clean and validate labels
# ---------------------------------------------------
print("\n🔍 Validating labels...")

# Convert to pandas Series for easy handling
y = pd.Series(y)

# Check for missing labels
if y.isnull().any():
    missing_count = y.isnull().sum()
    print(f"⚠️  WARNING: {missing_count} missing labels detected!")
    print("   Removing rows with missing labels...")
    
    # Remove rows with missing labels
    valid_indices = ~y.isnull()
    X = X[valid_indices]
    y = y[valid_indices]
    
    print(f"✅ After cleaning: {len(y)} samples remain")

# Map labels to binary (0/1)
# Handle both string and numeric formats
if y.dtype == 'object':
    label_mapping = {'Legitimate': 0, 'Phishing': 1}
    y = y.map(label_mapping)
    
    # Check if mapping was successful
    if y.isnull().any():
        print("❌ ERROR: Some labels couldn't be mapped!")
        print(f"   Unique values found: {y.unique()}")
        raise ValueError("Invalid label format. Expected 'Legitimate' or 'Phishing'")
else:
    # Already numeric - ensure it's 0/1
    if not set(y.unique()).issubset({0, 1}):
        print("❌ ERROR: Numeric labels must be 0 or 1")
        raise ValueError(f"Invalid numeric labels: {y.unique()}")

# Convert to numpy array
y = y.values

print(f"✅ Label distribution:")
unique, counts = np.unique(y, return_counts=True)
for label, count in zip(unique, counts):
    label_name = 'Legitimate' if label == 0 else 'Phishing'
    print(f"   {label_name}: {count} ({count/len(y)*100:.1f}%)")

# ---------------------------------------------------
# STEP 3: Train-test split (CRITICAL for no leakage)
# ---------------------------------------------------
print("\n📊 Splitting data into train/test sets...")

# 🔥 IMPORTANT: This split happens ONCE and test set is NEVER used for:
# - Hyperparameter tuning
# - Cross-validation
# - Model training
# Test set is ONLY used for final evaluation

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,       
    random_state=42,     
    stratify=y            
)

print(f"✅ Training set: {X_train.shape[0]} samples")
print(f"✅ Test set: {X_test.shape[0]} samples")

# Verify class distribution is maintained
train_dist = np.bincount(y_train) / len(y_train)
test_dist = np.bincount(y_test) / len(y_test)
print(f"\n   Train distribution: Legitimate={train_dist[0]:.1%}, Phishing={train_dist[1]:.1%}")
print(f"   Test distribution:  Legitimate={test_dist[0]:.1%}, Phishing={test_dist[1]:.1%}")

# ---------------------------------------------------
# STEP 4: Hyperparameter optimization using Optuna
# ---------------------------------------------------
print("\n" + "="*70)
print(" 🔍 HYPERPARAMETER OPTIMIZATION WITH OPTUNA")
print("="*70)

def objective(trial):
    """
    Optuna objective function for hyperparameter tuning
    
    🔥 CRITICAL: Uses ONLY training data with cross-validation
    Test set is NEVER touched during optimization
    
    Why this prevents data leakage:
    - Creates CV folds from X_train only
    - Each fold uses part of train for validation
    - Test set remains completely unseen
    - Returns average CV score (not test score)
    """
    
    # Suggest hyperparameters
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
    
    # Create model with suggested parameters
    model = XGBClassifier(**params)
    
    # 🔥 CRITICAL: Cross-validation on TRAINING data only
    # Uses StratifiedKFold to maintain class distribution in each fold
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # Get cross-validation scores (on training data only!)
    cv_scores = cross_val_score(
        model, X_train, y_train,
        cv=cv,
        scoring='accuracy',
        n_jobs=-1  # Use all CPU cores
    )
    
    # Return mean CV accuracy (Optuna maximizes this)
    return cv_scores.mean()


print("\n🎯 Starting Optuna optimization...")
print(f"   Running {40} trials to find best hyperparameters...")
print(f"   This may take several minutes...\n")

# Create Optuna study
study = optuna.create_study(
    direction="maximize",  # Maximize accuracy
    study_name="xgboost_2025_optimization"
)

# Run optimization
study.optimize(
    objective,
    n_trials=40,
    show_progress_bar=True,
    n_jobs=1  # Sequential trials (safer for XGBoost)
)

print("\n" + "="*70)
print(" 🎯 OPTIMIZATION COMPLETE")
print("="*70)
print(f"\n✅ Best CV Accuracy: {study.best_value:.4f}")
print(f"\n✅ Best Hyperparameters:")
for param, value in study.best_params.items():
    print(f"   {param}: {value}")

# ---------------------------------------------------
# STEP 5: Train final model with best parameters
# ---------------------------------------------------
print("\n" + "="*70)
print(" 🤖 TRAINING FINAL MODEL")
print("="*70)

print("\n🔧 Training model with optimized hyperparameters...")

# Create final model with best parameters
final_model = XGBClassifier(**study.best_params)

# 🔥 TRAIN ON TRAINING DATA ONLY

final_model = XGBClassifier(**study.best_params, eval_metric='logloss')

# Train model
final_model.fit(
    X_train, y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=False 
)
print("✅ Model training complete!")

# ---------------------------------------------------
# STEP 6: Cross-validation evaluation (on training data)
# ---------------------------------------------------
print("\n" + "="*70)
print(" 📊 CROSS-VALIDATION EVALUATION (Training Data)")
print("="*70)

# This shows how well the model generalizes within training data
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(
    final_model, X_train, y_train,
    cv=cv,
    scoring='accuracy',
    n_jobs=-1
)

print(f"\n✅ Cross-validation accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
print(f"   Fold scores: {[f'{score:.4f}' for score in cv_scores]}")

# ---------------------------------------------------
# STEP 7: Final evaluation on held-out test set
# ---------------------------------------------------
print("\n" + "="*70)
print(" 🧪 FINAL EVALUATION (Held-out Test Set)")
print("="*70)

# 🔥 FIRST TIME we use test set for evaluation
# This is the TRUE measure of model performance
y_pred_test = final_model.predict(X_test)
y_pred_proba_test = final_model.predict_proba(X_test)[:, 1]

test_accuracy = accuracy_score(y_test, y_pred_test)

print(f"\n✅ Test Set Accuracy: {test_accuracy:.4f}")

# Convert to labels for readable report
label_mapping = {0: 'Legitimate', 1: 'Phishing'}
y_test_labels = pd.Series(y_test).map(label_mapping)
y_pred_labels = pd.Series(y_pred_test).map(label_mapping)

print("\n📊 Classification Report:")
print(classification_report(y_test_labels, y_pred_labels, digits=4))

# Confusion matrix
print("\n📊 Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred_test)
print(f"   True Negatives (Legitimate correctly): {cm[0][0]}")
print(f"   False Positives (Legitimate as Phishing): {cm[0][1]}")
print(f"   False Negatives (Phishing as Legitimate): {cm[1][0]}")
print(f"   True Positives (Phishing correctly): {cm[1][1]}")

# ---------------------------------------------------
# STEP 8: Check for overfitting
# ---------------------------------------------------
print("\n" + "="*70)
print(" 🔍 OVERFITTING CHECK")
print("="*70)

# Train accuracy
y_pred_train = final_model.predict(X_train)
train_accuracy = accuracy_score(y_train, y_pred_train)

print(f"\n   Training accuracy: {train_accuracy:.4f}")
print(f"   Test accuracy:     {test_accuracy:.4f}")
print(f"   Difference:        {abs(train_accuracy - test_accuracy):.4f}")

# Analyze overfitting
diff = train_accuracy - test_accuracy
if diff < 0.02:
    print("\n✅ Good generalization - minimal overfitting")
elif diff < 0.05:
    print("\n⚠️  Slight overfitting detected (acceptable)")
elif diff < 0.10:
    print("\n⚠️  Moderate overfitting - consider regularization")
else:
    print("\n❌ Severe overfitting - model may not generalize well")
    print("   Suggestions:")
    print("   - Reduce max_depth")
    print("   - Increase min_child_weight")
    print("   - Increase reg_lambda/reg_alpha")
    print("   - Reduce n_estimators")

# ---------------------------------------------------
# STEP 9: Feature importance analysis
# ---------------------------------------------------
print("\n" + "="*70)
print(" 🎯 FEATURE IMPORTANCE")
print("="*70)

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': final_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n🏆 Top 15 Most Important Features:")
print(feature_importance.head(15).to_string(index=False))

# ---------------------------------------------------
# STEP 10: Save model and metadata
# ---------------------------------------------------
print("\n" + "="*70)
print(" 💾 SAVING MODEL")
print("="*70)

# Save final model
joblib.dump(final_model, "Models/2025/model_2025.pkl")

# Save feature list (CRITICAL for prediction pipeline)
feature_list = list(X.columns)
joblib.dump(feature_list, "Models/2025/features_2025.pkl")

# Save additional metadata
metadata = {
    'n_features': len(feature_list),
    'n_training_samples': len(X_train),
    'n_test_samples': len(X_test),
    'test_accuracy': float(test_accuracy),
    'cv_accuracy_mean': float(cv_scores.mean()),
    'cv_accuracy_std': float(cv_scores.std()),
    'best_params': study.best_params,
    'class_distribution': {
        'legitimate': int(np.sum(y == 0)),
        'phishing': int(np.sum(y == 1))
    }
}
joblib.dump(metadata, "Models/2025/model_2025_metadata.pkl")

print("\n✅ Saved files:")
print("   - model_2025.pkl (trained XGBoost model)")
print("   - features_2025.pkl (feature names list)")
print("   - model_2025_metadata.pkl (training metadata)")

# ---------------------------------------------------
# STEP 11: Final summary
# ---------------------------------------------------
print("\n" + "="*70)
print(" ✅ TRAINING COMPLETE - SUMMARY")
print("="*70)

print(f"\n📊 Model Performance:")
print(f"   Test Accuracy:          {test_accuracy:.4f}")
print(f"   CV Accuracy:            {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"   Overfitting Score:      {diff:.4f}")

print(f"\n📈 Dataset Statistics:")
print(f"   Total samples:          {len(X)}")
print(f"   Training samples:       {len(X_train)}")
print(f"   Test samples:           {len(X_test)}")
print(f"   Number of features:     {len(feature_list)}")

print(f"\n🎯 Best Hyperparameters:")
for param, value in list(study.best_params.items())[:5]:
    print(f"   {param}: {value}")

print("\n🎉 Model is ready for production use!")
print("   Load with: model = joblib.load('model_2025.pkl')")

print("\n" + "="*70)