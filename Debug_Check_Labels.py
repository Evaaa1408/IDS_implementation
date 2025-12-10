import joblib
import pandas as pd
import numpy as np
import sys
import os

# Add Data_Preprocessing to path
sys.path.append(os.path.join(os.path.dirname(__file__), "Data_Preprocessing"))

from feature_extractor import URLFeatureExtractor

# Paths
MODEL_2025_PATH = "Models/2025/model_2025.pkl"
MODEL_2023_PATH = "Models/2023/model_2023.pkl"

def test_model():
    print("🚀 LOADING MODELS...")
    try:
        model_2025 = joblib.load(MODEL_2025_PATH)
        print("✅ Model 2025 Loaded")
    except Exception as e:
        print(f"❌ Failed to load Model 2025: {e}")
        return

    # Test Case: SAFE BROWSING TEST SITE
    url = "https://testsafebrowsing.appspot.com/s/phishing.html"
    print(f"\nExample URL: {url}")
    
    # 1. Extract Features
    extractor = URLFeatureExtractor()
    features_25 = extractor.extract(url)
    df_25 = pd.DataFrame([features_25])
    
    print("\n🧐 Extracted Features:")
    print(df_25.T)
    
    # 2. Get Raw Probabilities
    probs = model_2025.predict_proba(df_25)[0]
    classes = model_2025.classes_
    
    print(f"📊 RAW OUTPUT (Model 2025): {probs}")
    print(f"   Classes: {classes}")
    print(f"   Prob[0]: {probs[0]:.4f}")
    print(f"   Prob[1]: {probs[1]:.4f}")
    
    if probs[1] > 0.9:
        print("\n⚠️  DIAGNOSIS: Index 1 is VERY HIGH for YouTube.")
        print("   If Index 1 = Phishing, the model thinks YouTube is Phishing (False Positive).")
        print("   If Index 1 = Legitimate, the mapping is inverted.")
    elif probs[0] > 0.9:
        print("\n✅ DIAGNOSIS: Index 0 is VERY HIGH for YouTube.")
        print("   If Index 0 = Legitimate, the model is correct.")

if __name__ == "__main__":
    test_model()
