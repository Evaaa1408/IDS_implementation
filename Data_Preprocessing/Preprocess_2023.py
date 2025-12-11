#Preprocess_2023.py
import pandas as pd

print("\n========================================")
print(" 🔍 PREPROCESSING — Dataset 2023 Cleaner")
print("========================================\n")

# ---------------------------------------------------
# 1) Load dataset
# ---------------------------------------------------
df = pd.read_csv("Dataset/LatestDataset2023.csv", encoding="utf-8", low_memory=False)

print("🔍 Original shape:", df.shape)
print("🔍 Original columns:", len(df.columns))

# ---------------------------------------------------
# 2) Clean column names
# ---------------------------------------------------
df.columns = df.columns.str.strip().str.replace(r"\s+", "", regex=True)

# ---------------------------------------------------
# 3) Remove duplicated columns
# ---------------------------------------------------
before = len(df.columns)
df = df.loc[:, ~df.columns.duplicated()]
after = len(df.columns)
print(f"🧹 Removed {before - after} duplicated columns")

# ---------------------------------------------------
# 4) Drop fully empty columns
# ---------------------------------------------------
null_cols = df.columns[df.isna().all()]
df = df.drop(columns=null_cols)

if len(null_cols) > 0:
    print(f"🗑 Dropped {len(null_cols)} empty columns")

# ---------------------------------------------------
# 5) Ensure label exists
# ---------------------------------------------------
if "label" not in df.columns:
    raise ValueError("❌ ERROR: 'label' column not found in dataset!")

df["label"] = pd.to_numeric(df["label"], errors="coerce")
if df["label"].isna().any():
    raise ValueError("❌ ERROR: Invalid label values found!")

# ---------------------------------------------------
# [Standardization] Flip labels to match Model 2025
# Current (2023): 0 = Phishing, 1 = Legitimate
# Target (2025):  1 = Phishing, 0 = Legitimate
# Action: Invert (1 - label)
# ---------------------------------------------------
print("\n🔄 Standardizing labels to match 2025 format (1=Phishing)...")
print("   Before: 0=Phishing, 1=Legitimate")
df["label"] = 1 - df["label"]
print("   After:  1=Phishing, 0=Legitimate")

# ---------------------------------------------------
# 6) Detect URL column
# ---------------------------------------------------
url_candidates = ["url", "URL", "Url", "link", "Link", "uri"]
url_col = None

for col in df.columns:
    if col.lower() in ["url", "link", "uri"]:
        url_col = col
        break

if not url_col:
    print("⚠️ WARNING: No URL column found — duplicate URL removal skipped.")
else:
    print(f"🌐 URL column detected: {url_col}")

    # ---------------------------------------------------
    # 7) Remove duplicate URLs
    # ---------------------------------------------------
    url_dupes = df.duplicated(subset=[url_col]).sum()
    print(f"\n🔍 Duplicate URLs before cleaning: {url_dupes}")

    df = df.drop_duplicates(subset=[url_col], keep="first")

    url_dupes_after = df.duplicated(subset=[url_col]).sum()
    print(f"🔍 Duplicate URLs after cleaning: {url_dupes_after}")

# ---------------------------------------------------
# 8) Remove fully identical rows
# ---------------------------------------------------
row_dupes = df.duplicated().sum()
print(f"\n🔍 Duplicate rows before cleaning: {row_dupes}")

df = df.drop_duplicates()

row_dupes_after = df.duplicated().sum()
print(f"🔍 Duplicate rows after cleaning: {row_dupes_after}")

minimal_drop_cols = [
    # dataset metadata
    "FILENAME", "filename"
    # direct leakage label-like scores
    "LikelinessIndex",
    "WAPLegitimate",
    "WAPPhishing",
    "URLSimilarityIndex",
    "URLSimilarity",
    "URLSimilarityScore",
    "URLCharProb",
    "URLCharProbScore",
    "DomainSimilarity",
    "IsUnreachable"
]

# keep only the columns that exist before dropping (safe)
to_drop = [c for c in minimal_drop_cols if c in df.columns]
if to_drop:
    print(f"\n Dropping {len(to_drop)} high-leakage / page-derived columns:")
    for c in to_drop:
        print(f"   - {c}")
    df = df.drop(columns=to_drop, errors="ignore")
else:
    print("\n No high-leakage columns found to drop.")

# ---------------------------------------------------
# 9) Shuffle dataset (remove ordering bias)
# ---------------------------------------------------
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# ---------------------------------------------------
# 10) Save cleaned dataset
# ---------------------------------------------------
df.to_csv("Dataset/LatestDataset2023.csv", index=False, encoding="utf-8")

print("\n========================================")
print(" ✅ CLEANING COMPLETE")
print("========================================")
print("New shape:", df.shape)
print("💾 Cleaned dataset successfully!\n")