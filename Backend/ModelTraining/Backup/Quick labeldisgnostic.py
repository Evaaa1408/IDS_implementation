"""
Quick diagnostic: Where did labels get inverted?
FIXED VERSION
"""
import pandas as pd
import joblib
import os
import sys

print("="*70)
print(" 🔍 QUICK LABEL CHECK (FIXED)")
print("="*70)

# ---------------------------------------------------------
# Check 1: Original dataset
# ---------------------------------------------------------
print("\n1️⃣ Checking Dataset_2025.csv (original):")
csv_path = "Dataset/Dataset_2025.csv"

if os.path.exists(csv_path):
    try:
        df_orig = pd.read_csv(csv_path)
        print(f"   Samples: {len(df_orig)}")
        print(f"   Label distribution: {df_orig['label'].value_counts().to_dict()}")
        
        # Handle string labels
        legit_sample = df_orig[df_orig['label'].isin(['Legitimate', 'legitimate', 0])]
        phish_sample = df_orig[df_orig['label'].isin(['Phishing', 'phishing', 1])] # Note: 2025 dataset usually uses 1 for phishing? Or strings?
        
        if not legit_sample.empty:
            print(f"   Sample Legitimate: {legit_sample['url'].iloc[0]}")
        else:
            print("   ⚠️ No Legitimate samples found")
            
        if not phish_sample.empty:
            print(f"   Sample Phishing:   {phish_sample['url'].iloc[0]}")
        else:
            print("   ⚠️ No Phishing samples found")
            
    except Exception as e:
        print(f"   ❌ Error reading CSV: {e}")
else:
    print(f"   ❌ File not found: {csv_path}")

# ---------------------------------------------------------
# Check 2: Features dataset (PKL output from feature_extract_2025.py)
# ---------------------------------------------------------
print("\n2️⃣ Checking features_2025.pkl & labels_2025.pkl (after feature extraction):")
# feature_extract_2025.py outputs .pkl files, not .csv
feat_path = "Models/2025/features_2025.pkl"
label_path = "Models/2025/labels_2025.pkl"

# Also check root if not in Models/2025
if not os.path.exists(feat_path):
    feat_path = "features_2025.pkl"
    label_path = "labels_2025.pkl"

if os.path.exists(feat_path) and os.path.exists(label_path):
    try:
        features = joblib.load(feat_path)
        labels = joblib.load(label_path)
        
        # Create a temp dataframe to visualize
        df_feat = pd.DataFrame(features)
        df_feat['label'] = labels
        
        # Add URLs if possible (features usually don't have URLs, but let's check basic stats)
        # We can't see URLs here unless we saved them or re-merge. 
        # But we can check the label mapping.
        
        print(f"   Samples: {len(df_feat)}")
        print(f"   Label distribution: {df_feat['label'].value_counts().to_dict()}")
        
        # Since we can't see URLs easily without re-merging, we at least check the counts and values
        print(f"   Labels in PKL are type: {type(labels[0])}")
        print(f"   Unique labels: {set(labels)}")
        
        print("\n   ⚠️ Note: PKL files don't store URLs by default, so we can't show sample URLs here.")
        print("   However, we can check if the counts match the CSV.")

    except Exception as e:
        print(f"   ❌ Error reading PKL: {e}")
else:
    print(f"   ❌ Files not found: {feat_path} or {label_path}")
    print("      (Did you run feature_extract_2025.py?)")


print("\n" + "="*70)
print(" 📝 ANALYSIS GUIDE")
print("="*70)
print("""
1. Check the 'Label distribution' in Step 1.
   - If 'Legitimate' > 'Phishing', but later in training you see inverted stats, there's a flip.

2. In Step 2 (PKL check):
   - Check if labels are 0 and 1.
   - Logic in feature_extract_2025.py was: labels.append(0 if row["label"]=="Legitimate" else 1)
   - So: 0 = Legitimate, 1 = Phishing.
   
   If you see 0 and 1 here, verify counts match Step 1.
   
   Legitimate Count (CSV) should ≈ Count of 0 (PKL)
   Phishing Count (CSV)   should ≈ Count of 1 (PKL)
   
   If they are swapped (e.g. Count of 0 ≈ Phishing Count), then the mapping is WRONG.
""")
