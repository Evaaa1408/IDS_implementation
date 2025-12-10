import pandas as pd
from feature_extractor import URLFeatureExtractor
import joblib
import os

# Path to cleaned dataset
csv_path = "Dataset\Dataset_2025.csv"

# Load cleaned dataset
df = pd.read_csv(csv_path)
print("Loaded cleaned dataset:", len(df))

# Drop rows with missing URL or label
df = df.dropna(subset=["url", "label"])
df = df[df["url"].str.strip() != ""] 
print("After dropping missing values:", len(df))

# Detect URL column
url_column = None
for col in df.columns:
    if "url" in col.lower():
        url_column = col
        break

if url_column is None:
    raise ValueError("URL column not found")

print("URL column =", url_column)

# Initialize feature extractor
extractor = URLFeatureExtractor()

# Extract features
feature_rows = []
labels = []

for idx, row in df.iterrows():
    url = str(row[url_column]).strip()
    features = extractor.extract(url)
    feature_rows.append(features)
    
    # The 2025 dataset should have a label column
    # Convert label to 0/1
    labels.append(0 if row["label"]=="Legitimate" else 1)

# Convert features to DataFrame
features_df = pd.DataFrame(feature_rows)

print("Extracted feature shape:", features_df.shape)

# Save features and labels as .pkl (used by training)
joblib.dump(features_df, "features_2025.pkl")
joblib.dump(labels, "labels_2025.pkl")

print("Saved features_2025.pkl and labels_2025.pkl")
