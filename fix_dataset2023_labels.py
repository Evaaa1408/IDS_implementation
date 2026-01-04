"""
Fix Dataset 2023 Label Reversal

This script inverts the labels in Dataset2023.csv:
- Current: Label 0 = Phishing (100,520), Label 1 = Legitimate (134,850)
- Fixed:   Label 0 = Legitimate (134,850), Label 1 = Phishing (100,520)

Aligns with PhiUSIIL dataset description.
"""

import pandas as pd
import os
from datetime import datetime

print("=" * 70)
print("FIXING DATASET 2023 LABEL REVERSAL")
print("=" * 70)

# Paths
input_file = 'datasets/dataset_2023/Dataset2023.csv'
output_file = 'datasets/dataset_2023/Dataset2023.csv'

# Load dataset
print(f"\n1. Loading dataset...")
df = pd.read_csv(input_file)
print(f"   Total rows: {len(df):,}")

# Check current distribution
label_0_before = len(df[df['label'] == 0])
label_1_before = len(df[df['label'] == 1])
print(f"\n2. Current label distribution:")
print(f"   Label 0: {label_0_before:,}")
print(f"   Label 1: {label_1_before:,}")

# Invert labels: 0→1, 1→0
print(f"\n3. Inverting labels...")
df['label'] = df['label'].apply(lambda x: 1 - x)

# Verify new distribution
label_0_after = len(df[df['label'] == 0])
label_1_after = len(df[df['label'] == 1])
print(f"\n4. New label distribution:")
print(f"   Label 0 (Legitimate): {label_0_after:,}")
print(f"   Label 1 (Phishing): {label_1_after:,}")

# Verify against expected
print(f"\n5. Verification:")
print(f"   Expected - Legitimate: 134,850")
print(f"   Actual - Label 0: {label_0_after:,}")
if label_0_after == 134850:
    print(f"   ✅ CORRECT! Labels are now properly aligned.")
else:
    print(f"   ⚠ Warning: Count doesn't match expected")

# Save corrected dataset
print(f"\n6. Saving corrected dataset...")
df.to_csv(output_file, index=False)
print(f"   ✓ Saved: {output_file}")

print("\n" + "=" * 70)
print("LABEL CORRECTION COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"\nNext steps:")
print(f"1. Retrain Model 2023 using: python training/Train_2023.py")
print(f"2. Verify predictions are now correct")
print("=" * 70)
