# FeatureExtract_2024.py - Extract features from Dataset_2024.csv
import pandas as pd
import joblib
import sys
import os

# Import from local Feature_Extractor.py
from Feature_Extractor import URLFeatureExtractor

print("="*70)
print(" 🔧 FEATURE EXTRACTION FOR DATASET 2024")
print("="*70)

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "..", "..", "datasets", "dataset_2024", "Dataset_2024.csv")

# Load dataset
print(f"\n📥 Loading dataset: {csv_path}")
df = pd.read_csv(csv_path)
print(f"✅ Loaded: {len(df)} URLs")

# Verify columns
print(f"   Columns: {list(df.columns)}")
if 'url' not in df.columns or 'label' not in df.columns:
    print("❌ ERROR: Expected columns 'url' and 'label'")
    exit(1)

# Verify label distribution
unique_labels = df['label'].unique()
print(f"   Unique labels: {unique_labels}")

label_counts = df['label'].value_counts()
print(f"\n📊 Label Distribution:")
for label, count in label_counts.items():
    label_name = "Legitimate" if label == 0 else "Phishing"
    print(f"   {label_name} ({label}): {count} ({count/len(df)*100:.1f}%)")

# ========================================================
# Extract Features
# ========================================================
print(f"\n🔧 Extracting URL features from {len(df)} URLs...")
extractor = URLFeatureExtractor()

feature_rows = []
labels = []
failed_count = 0

for idx, row in df.iterrows():
    if idx % 10000 == 0 and idx > 0:
        print(f"   Progress: {idx}/{len(df)} ({idx/len(df)*100:.1f}%)")
    
    url = str(row['url']).strip()
    
    try:
        features = extractor.extract(url)
        feature_rows.append(features)
        labels.append(int(row['label']))
    except Exception as e:
        failed_count += 1
        if failed_count <= 5:  # Show first 5 errors
            print(f"   ⚠️ Failed to extract features from: {url[:50]}... - {e}")

print(f"   Progress: {len(df)}/{len(df)} (100.0%)")

if failed_count > 0:
    print(f"\n⚠️  Failed to extract features from {failed_count} URLs ({failed_count/len(df)*100:.2f}%)")
    print(f"   Successfully extracted: {len(feature_rows)} URLs")

# Convert features to DataFrame
features_df = pd.DataFrame(feature_rows)

print(f"\n✅ Extracted features shape: {features_df.shape}")
print(f"✅ Number of features: {len(features_df.columns)}")
print(f"✅ Feature names: {list(features_df.columns)}")

# ========================================================
# Validate Labels
# ========================================================
print(f"\n🔍 Validating extracted labels...")
unique_labels = set(labels)
print(f"   Unique label values: {unique_labels}")

if unique_labels == {0, 1}:
    print(f"   ✅ Labels are binary (0 = Legitimate, 1 = Phishing)")
elif unique_labels == {0}:
    print(f"   ⚠️  WARNING: Only legitimate URLs (0)")
elif unique_labels == {1}:
    print(f"   ⚠️  WARNING: Only phishing URLs (1)")
else:
    print(f"   ❌ ERROR: Unexpected label values: {unique_labels}")
    exit(1)

label_counts = pd.Series(labels).value_counts()
print(f"\n   Label Distribution:")
for label, count in label_counts.items():
    label_name = "Legitimate" if label == 0 else "Phishing"
    print(f"     {label_name} ({label}): {count} ({count/len(labels)*100:.1f}%)")

# ========================================================
# Save
# ========================================================
output_dir = os.path.join(script_dir, "Features_Output")
os.makedirs(output_dir, exist_ok=True)

features_path = os.path.join(output_dir, "extracted_features_2024.pkl")
labels_path = os.path.join(output_dir, "extracted_labels_2024.pkl")

print(f"\n💾 Saving files to '{output_dir}/'...")
joblib.dump(features_df, features_path)
joblib.dump(labels, labels_path)

print(f"✅ Saved: extracted_features_2024.pkl (shape: {features_df.shape})")
print(f"✅ Saved: extracted_labels_2024.pkl (length: {len(labels)})")

# ========================================================
# Final Verification
# ========================================================
print(f"\n🔍 Final Verification:")
loaded_features = joblib.load(features_path)
loaded_labels = joblib.load(labels_path)

print(f"   Features shape: {loaded_features.shape}")
print(f"   Labels count: {len(loaded_labels)}")
print(f"   Labels unique: {set(loaded_labels)}")
print(f"   Match: {len(loaded_features) == len(loaded_labels)}")

# ========================================================
# Feature Statistics
# ========================================================
print(f"\n📊 Feature Statistics:")
print(f"   Total samples: {len(features_df)}")
print(f"   Total features: {len(features_df.columns)}")
print(f"\n   Sample feature values (first URL):")
for col in features_df.columns[:10]:  # Show first 10 features
    print(f"     {col}: {features_df[col].iloc[0]}")
if len(features_df.columns) > 10:
    print(f"     ... and {len(features_df.columns) - 10} more features")

print(f"\n" + "="*70)
print(" ✅ FEATURE EXTRACTION COMPLETE!")
print("="*70)

print(f"\n📁 Output files:")
print(f"   - {features_path}")
print(f"   - {labels_path}")
print(f"\n📊 Dataset Summary:")
print(f"   Total URLs: {len(features_df):,}")
print(f"   Legitimate: {label_counts.get(0, 0):,} ({label_counts.get(0, 0)/len(labels)*100:.1f}%)")
print(f"   Phishing: {label_counts.get(1, 0):,} ({label_counts.get(1, 0)/len(labels)*100:.1f}%)")
print(f"\n💡 Ready for model training with Train_2024.py!")
