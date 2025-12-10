import pandas as pd
import re

# Load raw dataset
df = pd.read_csv("Dataset\Dataset_2025.csv")
csv_path = "Dataset/Dataset_2025.csv" 
print("Original dataset size:", len(df))

# -------------------------------
# 1. Standardize column names
# -------------------------------
df.columns = df.columns.str.strip().str.lower()

# Ensure URL column exists
url_column = None
for col in df.columns:
    if "url" in col:
        url_column = col
        break

if url_column is None:
    raise ValueError("No URL column found in Dataset 2025!")

# -------------------------------
# 2. Remove duplicates
# -------------------------------
df = df.drop_duplicates(subset=[url_column])
print("After removing duplicates:", len(df))

# -------------------------------
# 3. Drop rows with missing URL
# -------------------------------
df = df.dropna(subset=[url_column])
print("After removing missing URLs:", len(df))

# -------------------------------
# 4. Clean whitespace / control characters
# -------------------------------
df[url_column] = df[url_column].astype(str).str.strip()
df[url_column] = df[url_column].str.replace(r"\s+", "", regex=True)

# -------------------------------
# 5. Remove clearly invalid URLs
# -------------------------------
def is_valid_url(u):
    pattern = re.compile(
        r'^(http|https)://'
        r'([A-Za-z0-9\-\.]+)'
    )
    return bool(pattern.match(u))

df = df[df[url_column].apply(is_valid_url)]
print("After removing invalid URLs:", len(df))

# -------------------------------
# 6. Save cleaned dataset
# -------------------------------
df.to_csv(csv_path, index=False)
print("✅ Cleaned Dataset_2025 has been overwritten successfully!")
