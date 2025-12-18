# Test_Phis.py - Test Phishing Pattern Model
import joblib
import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Changed_Solution.Changed_feature_extractor import ChangedURLFeatureExtractor

print("\n" + "="*70)
print(" 🧪 TESTING PHISHING PATTERN MODEL")
print("="*70)

# ========================================================
# 1. Load Model and Metadata
# ========================================================
model_path = "Phishing_Model_Output/phishing_pattern_model.pkl"
features_list_path = "Phishing_Model_Output/feature_names.pkl"
metadata_path = "Phishing_Model_Output/model_metadata.pkl"

print(f"\n📥 Loading model...")
model = joblib.load(model_path)
feature_names = joblib.load(features_list_path)
metadata = joblib.load(metadata_path)

print(f"✅ Model loaded successfully!")
print(f"   Features: {metadata['n_features']}")
print(f"   Trained on: {metadata['n_samples']:,} phishing URLs")
print(f"   Test accuracy: {metadata['test_accuracy']*100:.2f}%")

# ========================================================
# 2. Initialize Feature Extractor
# ========================================================
extractor = ChangedURLFeatureExtractor()

# ========================================================
# 3. Test URLs
# ========================================================
test_urls = [
    # Known Phishing Patterns
    ("http://paypa1-secure-login.tk", "Phishing"),
    ("https://g00gle-verify.xyz", "Phishing"),
    ("http://faceboook-security.com", "Phishing"),
    ("https://secure-apple-id-verify.tk", "Phishing"),
    ("http://bankofamerica-secure.ml", "Phishing"),
    ("https://login-netflix-update.cf", "Phishing"),
    ("http://amaz0n-account-verify.gq", "Phishing"),
    ("https://secure-payment-paypal123.click", "Phishing"),
    
    # Legitimate URLs (for comparison)
    ("https://www.google.com", "Legitimate"),
    ("https://www.facebook.com", "Legitimate"),
    ("https://www.amazon.com", "Legitimate"),
    ("https://www.paypal.com", "Legitimate"),
    ("https://www.apple.com", "Legitimate"),
    ("https://www.netflix.com", "Legitimate"),
    ("https://github.com/openai/gpt-4", "Legitimate"),
    ("https://docs.google.com/document/d/123/edit", "Legitimate"),
    
    # Complex Legitimate URLs
    ("https://www.britannica.com/biography/Che-Guevara", "Legitimate"),
    ("https://scholar.google.com/scholar?q=phishing+detection", "Legitimate"),
    ("https://learn.microsoft.com/en-us/azure/active-directory", "Legitimate"),
    ("https://developer.mozilla.org/en-US/docs/Web/JavaScript", "Legitimate"),
]

# ========================================================
# 4. Run Tests
# ========================================================
print(f"\n🔍 Testing {len(test_urls)} URLs...")
print("="*90)

results = []

for url, expected_type in test_urls:
    # Extract features
    features = extractor.extract(url)
    features_df = pd.DataFrame([features])
    
    # Ensure feature order matches training
    features_df = features_df[feature_names]
    
    # Predict
    prediction = model.predict(features_df)[0]
    probability = model.predict_proba(features_df)[0, 1]  # Probability of phishing
    
    # Determine result
    predicted_type = "Phishing" if probability > 0.5 else "Legitimate"
    match = "✅" if predicted_type == expected_type else "❌"
    
    results.append({
        'url': url,
        'expected': expected_type,
        'predicted': predicted_type,
        'probability': probability,
        'match': match
    })
    
    # Display result
    url_display = url if len(url) <= 60 else url[:57] + "..."
    print(f"\n{match} {expected_type:12s} | Prob: {probability:.4f} | {predicted_type:12s}")
    print(f"   {url_display}")

# ========================================================
# 5. Summary Statistics
# ========================================================
results_df = pd.DataFrame(results)

print(f"\n" + "="*90)
print(" 📊 TEST SUMMARY")
print("="*90)

total = len(results_df)
correct = (results_df['match'] == '✅').sum()
accuracy = correct / total * 100

print(f"\n✅ Overall Accuracy: {correct}/{total} ({accuracy:.2f}%)")

# Breakdown by type
print(f"\n📋 Breakdown by Expected Type:")
for exp_type in ['Phishing', 'Legitimate']:
    subset = results_df[results_df['expected'] == exp_type]
    if len(subset) > 0:
        correct_subset = (subset['match'] == '✅').sum()
        total_subset = len(subset)
        acc_subset = correct_subset / total_subset * 100
        print(f"   {exp_type:12s}: {correct_subset}/{total_subset} correct ({acc_subset:.2f}%)")

# Show misclassifications
misclassified = results_df[results_df['match'] == '❌']
if len(misclassified) > 0:
    print(f"\n⚠️  Misclassified URLs ({len(misclassified)}):")
    for idx, row in misclassified.iterrows():
        url_display = row['url'] if len(row['url']) <= 60 else row['url'][:57] + "..."
        print(f"   Expected: {row['expected']:12s} | Predicted: {row['predicted']:12s} | Prob: {row['probability']:.4f}")
        print(f"   {url_display}")
else:
    print(f"\n🎉 No misclassifications! Perfect score!")

# Probability distribution
print(f"\n📊 Probability Distribution:")
phishing_probs = results_df[results_df['expected'] == 'Phishing']['probability']
legit_probs = results_df[results_df['expected'] == 'Legitimate']['probability']

if len(phishing_probs) > 0:
    print(f"   Phishing URLs:")
    print(f"     Mean: {phishing_probs.mean():.4f}")
    print(f"     Min:  {phishing_probs.min():.4f}")
    print(f"     Max:  {phishing_probs.max():.4f}")

if len(legit_probs) > 0:
    print(f"   Legitimate URLs:")
    print(f"     Mean: {legit_probs.mean():.4f}")
    print(f"     Min:  {legit_probs.min():.4f}")
    print(f"     Max:  {legit_probs.max():.4f}")

print(f"\n" + "="*90)
print(" ✅ TESTING COMPLETE!")
print("="*90)

# ========================================================
# 6. Interactive Testing (Optional)
# ========================================================
print(f"\n💡 Want to test a custom URL?")
print(f"   Usage: python Test_Phis.py <url>")
print(f"   Example: python Test_Phis.py https://paypa1-verify.tk")

if len(sys.argv) > 1:
    custom_url = sys.argv[1]
    print(f"\n🔍 Testing custom URL: {custom_url}")
    
    try:
        features = extractor.extract(custom_url)
        features_df = pd.DataFrame([features])
        features_df = features_df[feature_names]
        
        prediction = model.predict(features_df)[0]
        probability = model.predict_proba(features_df)[0, 1]
        
        predicted_type = "Phishing" if probability > 0.5 else "Legitimate"
        
        print(f"\n📊 Result:")
        print(f"   Prediction: {predicted_type}")
        print(f"   Phishing Probability: {probability:.4f} ({probability*100:.2f}%)")
        
        if probability > 0.8:
            print(f"   ⚠️  HIGH RISK - Very likely phishing!")
        elif probability > 0.5:
            print(f"   ⚠️  MEDIUM RISK - Possibly phishing")
        else:
            print(f"   ✅ LOW RISK - Likely legitimate")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
