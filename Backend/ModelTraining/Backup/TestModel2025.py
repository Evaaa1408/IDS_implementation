import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from Data_Preprocessing.feature_extractor import URLFeatureExtractor
import pandas as pd
import joblib

print("="*70)
print(" 🧪 TESTING MODEL 2025 WHITELIST")
print("="*70)

# Load model (assuming running from project root or paths relative to project root)
# If running from script location, we might need to adjust, but let's try relative to CWD first if CWD is project root.
# Utilizing the same logic as sys.path to find 'Models' folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
model_path = os.path.join(project_root, 'Models/2025/model_2025.pkl')
features_path = os.path.join(project_root, 'Models/2025/features_2025.pkl')

model = joblib.load(model_path)
features = joblib.load(features_path)
extractor = URLFeatureExtractor()

test_urls = [
    "https://www.youtube.com",
    "https://www.instagram.com",
    "https://www.google.com",
    "https://github.com",
]

print("\n🔍 Testing Whitelist:\n")
for url in test_urls:
    feats = extractor.extract(url)
    
    # Check if whitelisted
    import tldextract
    ext = tldextract.extract(url)
    domain = f"{ext.domain}.{ext.suffix}"
    is_legit = extractor.is_legitimate_domain(domain)
    
    # Check features
    suspicious_features = ['CharacterSubstitutions', 'TyposquattingScore', 'KnownTyposquatting', 'Combosquatting', 'SuspiciousTLD']
    suspicious_count = sum(feats.get(f, 0) for f in suspicious_features)
    
    # Predict
    df = pd.DataFrame([feats]).reindex(columns=features, fill_value=0)
    prob = model.predict_proba(df)[0]
    
    print(f"URL: {url}")
    print(f"  Is Whitelisted: {is_legit}")
    print(f"  Suspicious Features: {suspicious_count}")
    print(f"  Model Prediction: {prob[1]:.4f} (phishing prob)")
    
    if is_legit and prob[1] > 0.5:
        print(f"  ❌ ERROR: Whitelisted site flagged as phishing!")
    elif not is_legit and prob[1] < 0.5:
        print(f"  ⚠️  WARNING: Non-whitelisted legit site marked safe")
    else:
        print(f"  ✅ OK")
    print()

print("="*70)
print("If whitelisted sites are flagged, the whitelist isn't working!")
print("="*70)