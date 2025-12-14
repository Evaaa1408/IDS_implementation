#feature_extract_2025.py
import pandas as pd
from feature_extractor import URLFeatureExtractor
import joblib
import os

print("="*70)
print(" 🔧 FEATURE EXTRACTION FOR MODEL 2025")
print("="*70)

# Path to cleaned dataset
csv_path = "Dataset/Dataset_2025.csv"

# Load cleaned dataset
df = pd.read_csv(csv_path)
print(f"\n✅ Loaded dataset: {len(df)} samples")

# Drop rows with missing URL or label
df = df.dropna(subset=["url", "label"])
df = df[df["url"].str.strip() != ""] 
print(f"✅ After dropping missing values: {len(df)} samples")

# Detect URL column
url_column = None
for col in df.columns:
    if "url" in col.lower():
        url_column = col
        break

if url_column is None:
    raise ValueError("❌ URL column not found!")

print(f"✅ URL column: {url_column}")

# ========================================================
# CRITICAL: Standardize label format
# ========================================================
print(f"\n🏷️  Processing Labels...")
print(f"   Original label dtype: {df['label'].dtype}")
print(f"   Original label values: {df['label'].unique()}")

# Standardize labels to numeric format
if df['label'].dtype == 'object':
    # Labels are strings
    print(f"   Converting string labels to numeric...")
    label_mapping = {
        'Legitimate': 0,
        'Phishing': 1,
        'legitimate': 0,  # Handle lowercase
        'phishing': 1,    # Handle lowercase
        'Safe': 0,
        'Malicious': 1
    }
    df['label'] = df['label'].map(label_mapping)
    
    # Check for unmapped values
    if df['label'].isnull().any():
        unmapped = df[df['label'].isnull()]['label'].unique()
        print(f"   ⚠️  Warning: Found unmapped label values: {unmapped}")
        print(f"   Dropping {df['label'].isnull().sum()} rows with unmapped labels...")
        df = df.dropna(subset=['label'])
else:
    # Labels are already numeric
    print(f"   Labels are already numeric")
    # Verify they're 0 or 1
    if not set(df['label'].unique()).issubset({0, 1}):
        print(f"   ⚠️  Warning: Labels are not 0/1. Mapping...")
        # Assume anything != 0 is phishing
        df['label'] = (df['label'] != 0).astype(int)

# Convert to integer
df['label'] = df['label'].astype(int)

print(f"\n✅ Final Label Distribution:")
print(f"   Legitimate (0): {(df['label'] == 0).sum()} ({(df['label'] == 0).sum()/len(df)*100:.1f}%)")
print(f"   Phishing (1):   {(df['label'] == 1).sum()} ({(df['label'] == 1).sum()/len(df)*100:.1f}%)")

# ========================================================
# Extract Features
# ========================================================
print(f"\n🔧 Extracting URL features...")
extractor = URLFeatureExtractor()

feature_rows = []
labels = []

for idx, row in df.iterrows():
    if idx % 10000 == 0:
        print(f"   Progress: {idx}/{len(df)} ({idx/len(df)*100:.1f}%)")
    
    url = str(row[url_column]).strip()
    features = extractor.extract(url)
    feature_rows.append(features)
    
    # CRITICAL: Use the already-processed numeric label
    labels.append(int(row["label"]))

# Convert features to DataFrame
features_df = pd.DataFrame(feature_rows)

print(f"\n✅ Extracted features shape: {features_df.shape}")
print(f"✅ Number of features: {len(features_df.columns)}")

# ========================================================
# Validate Labels
# ========================================================
print(f"\n🔍 Validating extracted labels...")
unique_labels = set(labels)
print(f"   Unique label values: {unique_labels}")

if unique_labels == {0, 1}:
    print(f"   ✅ Labels are correct: 0=Legitimate, 1=Phishing")
elif unique_labels == {1, 0}:
    print(f"   ✅ Labels are correct: 0=Legitimate, 1=Phishing")
else:
    print(f"   ❌ ERROR: Invalid labels found!")
    exit(1)

label_counts = pd.Series(labels).value_counts()
print(f"\n   Label Distribution:")
print(f"     0 (Legitimate): {label_counts.get(0, 0)}")
print(f"     1 (Phishing):   {label_counts.get(1, 0)}")

# ========================================================
# Save
# ========================================================
print(f"\n💾 Saving files...")
joblib.dump(features_df, "features_2025.pkl")
joblib.dump(labels, "labels_2025.pkl")

print(f"✅ Saved: features_2025.pkl")
print(f"✅ Saved: labels_2025.pkl")

# ========================================================
# Final Verification
# ========================================================
print(f"\n🔍 Final Verification:")
loaded_features = joblib.load("Models/2025/features_2025.pkl")
loaded_labels = joblib.load("Models/2025/labels_2025.pkl")

print(f"   Features shape: {loaded_features.shape}")
print(f"   Labels count: {len(loaded_labels)}")
print(f"   Labels unique: {set(loaded_labels)}")
print(f"   Match: {len(loaded_features) == len(loaded_labels)}")

print(f"\n" + "="*70)
print(" ✅ FEATURE EXTRACTION COMPLETE!")
print("="*70)