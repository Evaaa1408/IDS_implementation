import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from feature_extract_2023 import Extractor2023
import os
import warnings
warnings.filterwarnings("ignore")

# --- CONFIG
CSV_PATH = "Dataset\LatestDataset2023.csv"
MODEL_OUT = "Models/2023/model_2023_url.pkl"
FEATURES_OUT = "Models/2023/features_2023_url.pkl"
os.makedirs("Models/2023", exist_ok=True)

# Load dataset
df = pd.read_csv(CSV_PATH, low_memory=False)
if 'URL' in df.columns:
    url_col = 'URL'
elif 'url' in df.columns:
    url_col = 'url'
else:
    raise ValueError("No URL column found in LatestDataset2023.csv")

# ensure label exists
if 'label' not in df.columns and 'Label' not in df.columns and 'Type' not in df.columns:
    raise ValueError("No label column found")

label_col = 'label' if 'label' in df.columns else ('Label' if 'Label' in df.columns else 'Type')
y_raw = df[label_col].astype(str).str.strip()

# map labels to 0/1
y = y_raw.map(lambda v: 0 if v.lower() in ['legitimate','0','benign','clean'] else 1)

# Extract features
extractor = Extractor2023()
rows = []
labels = []
for idx, r in df.iterrows():
    u = str(r[url_col]).strip()
    if not u:
        continue
    rows.append(extractor.extract(u))
    labels.append(y.iloc[idx])

X = pd.DataFrame(rows)
y = np.array(labels, dtype=int)

print("Feature shape:", X.shape, "Labels:", y.shape)

# drop columns with zero variance
X = X.loc[:, X.nunique() > 1]

# train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# quick hyperparam search (small)
param_distributions = {
    "n_estimators": [200, 300, 400],
    "max_depth": [8, 12, 16, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ['sqrt', 'log2']
}
rf = RandomForestClassifier(n_jobs=-1, random_state=42)
search = RandomizedSearchCV(rf, param_distributions, n_iter=20, cv=3, scoring='accuracy', n_jobs=-1, random_state=42)
search.fit(X_train, y_train)
best = search.best_estimator_

# evaluate
print("\nCV mean (approx):", search.best_score_)
y_pred = best.predict(X_test)
print("Test acc:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# save
joblib.dump(best, MODEL_OUT)
joblib.dump(list(X.columns), FEATURES_OUT)
print("Saved model and feature list.")
