import pandas as pd
from sklearn.model_selection import train_test_split

print("\n========================================================")
print(" 🔍 DATA LEAKAGE DIAGNOSTIC TOOL — Model 2023 Dataset")
print("========================================================\n")

# -------------------------------------------------------
# 1. LOAD DATA
# -------------------------------------------------------
df = pd.read_csv("Dataset/LatestDataset2023.csv")

print(f"Dataset shape: {df.shape}")
print(f"Columns: {len(df.columns)}\n")

# Normalize column names (lowercase)
df.columns = [col.lower().strip() for col in df.columns]

# Identify correct URL column
url_col = None
for candidate in ["url", "urls", "link", "uri"]:
    if candidate in df.columns:
        url_col = candidate
        break

# Identify label column
label_col = "label" if "label" in df.columns else None

# -------------------------------------------------------
# 2. CHECK DUPLICATE URLS
# -------------------------------------------------------
if url_col:
    dup_total = df.duplicated(subset=[url_col]).sum()
    print(f"🔍 Total duplicated URLs: {dup_total}")
else:
    print("⚠️ No URL-like column found — cannot check URL duplicates.")

# -------------------------------------------------------
# 3. CHECK FEATURE CORRELATION WITH LABEL
# -------------------------------------------------------
print("\n🔍 Checking feature correlation with Label...")

num_df = df.select_dtypes(include=['int64', 'float64'])
correlation = num_df.corr()[label_col].sort_values(ascending=False)

print(correlation)

perfect_corr = correlation[(correlation.abs() == 1.0)]
high_corr = correlation[(correlation.abs() > 0.95) & (correlation.abs() < 1.0)]

if len(perfect_corr) > 1:
    print("\n🚨 PERFECT correlation with Label detected!")
    print(perfect_corr)

if len(high_corr) > 0:
    print("\n⚠️ HIGH correlation features (>0.95):")
    print(high_corr)

# -------------------------------------------------------
# 4. CHECK IF DATASET IS SORTED
# -------------------------------------------------------
print("\n🔍 Checking if dataset is sorted by label...")

head_labels = df[label_col].head(20).tolist()
tail_labels = df[label_col].tail(20).tolist()

print(f"First 20 labels: {head_labels}")
print(f"Last 20 labels: {tail_labels}")

if len(set(head_labels)) == 1 or len(set(tail_labels)) == 1:
    print("\n⚠️ Dataset appears sorted — shuffle before splitting.")
else:
    print("\n✅ Dataset looks shuffled.")

# -------------------------------------------------------
# 5. TRAIN/TEST LABEL DISTRIBUTION CHECK
# -------------------------------------------------------
print("\n🔍 Checking label distribution consistency...")

X = df.drop(columns=[label_col])
y = df[label_col]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("\nLabel distribution (original):")
print(y.value_counts(normalize=True))

print("\nLabel distribution (train):")
print(y_train.value_counts(normalize=True))

print("\nLabel distribution (test):")
print(y_test.value_counts(normalize=True))

# -------------------------------------------------------
# 6. TRAIN/TEST URL OVERLAP CHECK
# -------------------------------------------------------
if url_col:
    print("\n🔍 Checking Train/Test URL overlap...")

    train_urls = set(X_train[url_col])
    test_urls = set(X_test[url_col])

    overlap = len(train_urls.intersection(test_urls))
    print(f"🚨 URL overlap between Train/Test: {overlap}")

    if overlap > 0:
        print("❌ URL leakage detected! Remove duplicates or group-split by URL.")
    else:
        print("✅ No URL overlap detected — safe.")
else:
    print("\n⚠️ Cannot check URL overlap (no URL column).")

print("\n========================================================")
print(" 🔍 LEAKAGE CHECK COMPLETE")
print("========================================================\n")
