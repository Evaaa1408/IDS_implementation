import pandas as pd

def preprocess_ensemble_dataset(file_path="Dataset\ensemble_dataset_2024.csv"):
    # ---------------------------------------
    # 1. Load dataset
    # ---------------------------------------
    df = pd.read_csv(file_path)

    # ---------------------------------------
    # 2. Standardize column names
    # ---------------------------------------
    df.columns = df.columns.str.strip().str.lower()

    rename_map = {
        "url": "url",
        "type": "label"
    }

    df = df.rename(columns=rename_map)

    # Ensure required columns exist:
    if "url" not in df or "label" not in df:
        raise ValueError("Dataset must contain URL and label columns.")

    # ---------------------------------------
    # 3. Drop duplicate rows
    # ---------------------------------------
    before_dup = len(df)
    df = df.drop_duplicates()
    after_dup = len(df)
    print(f"Removed {before_dup - after_dup} duplicate rows.")

    # ---------------------------------------
    # 4. Drop duplicate URLs only
    # ---------------------------------------
    before_url = len(df)
    df = df.drop_duplicates(subset=["url"])
    after_url = len(df)
    print(f"Removed {before_url - after_url} duplicate URLs.")

    # ---------------------------------------
    # 5. Clean/convert labels
    # ---------------------------------------
    df["label"] = df["label"].astype(str).str.lower().str.strip()

    df["label"] = df["label"].replace({
        "legitimate": 0,
        "benign": 0,
        "good": 0,
        "phishing": 1,
        "malicious": 1,
        "bad": 1
    })

    # Convert to numeric (in case some values are still text)
    df["label"] = pd.to_numeric(df["label"], errors="coerce")

    # Remove rows where label is invalid
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)

    # ---------------------------------------
    # 6. Shuffle rows
    # ---------------------------------------
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # ---------------------------------------
    # 7. Overwrite the original dataset
    # ---------------------------------------
    df.to_csv(file_path, index=False)
    print(f"Cleaning complete. Cleaned dataset saved to {file_path}.")

    return df


if __name__ == "__main__":
    preprocess_ensemble_dataset()
