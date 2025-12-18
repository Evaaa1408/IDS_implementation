# Preprocess_2024.py - Clean Dataset_2024.csv
import pandas as pd
import os

print("\n" + "="*70)
print(" 🔧 DATASET 2024 PREPROCESSING")
print("="*70)

# Path to dataset
csv_path = "Learn_Model_2024\Dataset_2024.csv"

# Check if file exists
if not os.path.exists(csv_path):
    print(f"\n❌ ERROR: File '{csv_path}' not found!")
    print(f"   Please make sure the file is in: {os.path.abspath(csv_path)}")
    exit(1)

# ========================================================
# 1. Load the dataset
# ========================================================
print(f"\n📥 Loading dataset from: {csv_path}")
df = pd.read_csv(csv_path)

print(f"✅ Loaded: {len(df)} rows, {len(df.columns)} columns")
print(f"   Columns: {list(df.columns)}")

# ========================================================
# 2. Display initial statistics
# ========================================================
print(f"\n📊 Initial Dataset Statistics:")
print(f"   Total rows: {len(df)}")
print(f"   Columns: {list(df.columns)}")
print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Check for missing values
missing_counts = df.isnull().sum()
if missing_counts.any():
    print(f"\n⚠️  Missing values found:")
    for col, count in missing_counts[missing_counts > 0].items():
        print(f"   {col}: {count} ({count/len(df)*100:.2f}%)")

# ========================================================
# 3. Check what columns exist (flexible approach)
# ========================================================
print(f"\n🔍 Detecting dataset structure...")

# Common column name variations
url_col = None
label_col = None

# Look for URL column
for col in df.columns:
    col_lower = col.lower()
    if 'url' in col_lower:
        url_col = col
        break

# Look for label column
for col in df.columns:
    col_lower = col.lower()
    if 'label' in col_lower or 'class' in col_lower or 'type' in col_lower:
        label_col = col
        break

if url_col is None:
    print(f"❌ ERROR: No URL column found!")
    print(f"   Available columns: {list(df.columns)}")
    exit(1)

print(f"✅ URL column: '{url_col}'")
if label_col:
    print(f"✅ Label column: '{label_col}'")
else:
    print(f"⚠️  No label column found - will keep all columns")

# ========================================================
# 4. Clean URL data
# ========================================================
print(f"\n🔧 Step 1: Cleaning URL data...")

# Remove rows with missing URLs
initial_count = len(df)
df = df.dropna(subset=[url_col])
print(f"   Removed {initial_count - len(df)} rows with missing URLs")

# Strip whitespace from URLs
df[url_col] = df[url_col].str.strip()

# Remove empty URLs
initial_count = len(df)
df = df[df[url_col] != '']
print(f"   Removed {initial_count - len(df)} rows with empty URLs")

print(f"   ✅ Cleaned URLs: {len(df)} remaining")

# ========================================================
# 5. Remove duplicate rows (entire row)
# ========================================================
print(f"\n🔧 Step 2: Removing duplicate rows...")
initial_count = len(df)
df = df.drop_duplicates()
duplicates_removed = initial_count - len(df)

print(f"   Duplicate rows removed: {duplicates_removed} ({duplicates_removed/initial_count*100:.2f}%)")
print(f"   ✅ Unique rows: {len(df)}")

# ========================================================
# 6. Remove duplicate URLs (keep first occurrence)
# ========================================================
print(f"\n🔧 Step 3: Removing duplicate URLs...")
initial_count = len(df)
df = df.drop_duplicates(subset=[url_col], keep='first')
url_duplicates_removed = initial_count - len(df)

print(f"   Duplicate URLs removed: {url_duplicates_removed} ({url_duplicates_removed/initial_count*100:.2f}%)")
print(f"   ✅ Unique URLs: {len(df)}")

# ========================================================
# 7. Final Dataset Info
# ========================================================
print(f"\n📊 Final Dataset Statistics:")
print(f"   Total rows: {len(df)}")
print(f"   Columns: {list(df.columns)}")
print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Display label distribution if exists
if label_col and label_col in df.columns:
    print(f"\n🏷️  Label Distribution:")
    label_counts = df[label_col].value_counts()
    for label, count in label_counts.items():
        print(f"   {label}: {count} ({count/len(df)*100:.2f}%)")

# ========================================================
# 8. Save cleaned dataset (OVERWRITE original)
# ========================================================
print(f"\n💾 Overwriting original file: {csv_path}")
df.to_csv(csv_path, index=False)

print(f"✅ Saved: {len(df)} rows, {len(df.columns)} columns")

# ========================================================
# 9. Verification
# ========================================================
print(f"\n🔍 Verification:")
loaded_df = pd.read_csv(csv_path)
print(f"   Loaded rows: {len(loaded_df)}")
print(f"   Loaded columns: {list(loaded_df.columns)}")
print(f"   Expected rows: {len(df)}")
print(f"   Match: {'✅ Yes' if len(loaded_df) == len(df) else '❌ No'}")

print(f"\n" + "="*70)
print(" ✅ PREPROCESSING COMPLETE!")
print("="*70)
print(f"\n📁 File updated: {os.path.abspath(csv_path)}")
print(f"   Total rows after cleaning: {len(df):,}")
print(f"   Total duplicates removed: {duplicates_removed + url_duplicates_removed:,}")
