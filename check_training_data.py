#!/usr/bin/env python3
"""
Check how many samples are actually in the training files
"""
import joblib

print("\n=== CHECKING TRAINING DATA ===\n")

# Load the actual training files
X = joblib.load("features_2025.pkl")
y = joblib.load("labels_2025.pkl")

print(f"📊 Features shape: {X.shape}")
print(f"   - Samples: {X.shape[0]:,}")
print(f"   - Features per sample: {X.shape[1]}")

print(f"\n📊 Labels count: {len(y):,}")

print(f"\n✅ Data is in PKL format (used for training)")
print(f"   The CSV file (dataset_2025.csv) is NOT used for training")

# Show breakdown
from collections import Counter
counts = Counter(y)
print(f"\n📊 Label distribution:")
print(f"   Legitimate (0): {counts[0]:,}")
print(f"   Phishing (1): {counts[1]:,}")
print(f"   Total: {len(y):,}")
