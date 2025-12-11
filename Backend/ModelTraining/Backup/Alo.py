import pandas as pd

df = pd.read_csv("Dataset/Dataset_2025.csv")

# If labels are strings
if df['label'].dtype == 'object':
    print("✅ Labels are strings - should be fine")
    print(df['label'].value_counts())
else:
    # If numeric, check encoding
    print("⚠️ Labels are numeric")
    print(df['label'].value_counts())
    
    # Sample a few safe domains
    google = df[df['url'].str.contains('google', case=False, na=False)]
    if len(google) > 0:
        print(f"\nGoogle URLs have label: {google['label'].mode()[0]}")
        print("Expected: 0 (Legitimate) or 'Legitimate'")