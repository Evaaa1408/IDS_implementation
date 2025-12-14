import sys
import os
import pandas as pd
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data_Preprocessing.feature_extractor import URLFeatureExtractor

print("\n" + "="*70)
print(" 🧪 VALIDATING PATTERN LEARNING - MODEL 2025")
print("="*70)

# Load retrained model
print("\n📥 Loading retrained model...")
try:
    model = joblib.load("Models/2025/model_2025.pkl")
    feature_names = joblib.load("Models/2025/features_2025.pkl")
    print("✅ Model loaded successfully")
except FileNotFoundError:
    print("❌ ERROR: Model not found. Please train the model first.")
    sys.exit(1)

extractor = URLFeatureExtractor()

# ============================================================
# TEST SET 1: Unseen Legitimate Sites
# ============================================================
print("\n" + "="*70)
print(" TEST 1: UNSEEN LEGITIMATE SITES")
print("="*70)
print("Expected: Low risk (\u003c30%) for all")
print()

unseen_legitimate = [
    ("https://claude.ai", "AI tool"),
    ("https://www.geeksforgeeks.org", "Educational site"),
    ("https://apspace.apu.edu.my", "University portal"),
    ("https://www.notion.so", "SaaS tool"),
    ("https://chat.openai.com", "AI tool"),
    ("https://www.stackoverflow.com", "Developer forum"),
    ("https://www.reddit.com", "Social media"),
    ("https://www.medium.com", "Publishing platform"),
    ("https://www.canva.com", "Design tool"),
    ("https://www.figma.com", "Design tool"),
]

test1_passed = 0
test1_total = len(unseen_legitimate)

for url, description in unseen_legitimate:
    feats = extractor.extract(url)
    df = pd.DataFrame([feats])
    df = df.reindex(columns=feature_names, fill_value=0)
    
    prob = model.predict_proba(df)[0][1]
    risk_pct = prob * 100
    
    # Check if whitelisted (bypass model)
    domain = url.lower().replace("https://", "").replace("http://", "").split("/")[0]
    is_whitelisted = extractor.is_legitimate_domain(domain)
    
    if is_whitelisted:
        status = "✅ PASS (Whitelisted)"
        test1_passed += 1
    elif risk_pct < 30:
        status = "✅ PASS"
        test1_passed += 1
    else:
        status = "❌ FAIL (Too high risk)"
    
    print(f"{status:20} {risk_pct:5.1f}% - {description:25} {url}")

print(f"\nTest 1 Result: {test1_passed}/{test1_total} passed ({test1_passed/test1_total*100:.0f}%)")

# ============================================================
# TEST SET 2: Known Phishing Patterns
# ============================================================
print("\n" + "="*70)
print(" TEST 2: KNOWN PHISHING PATTERNS")
print("="*70)
print("Expected: High risk (\u003e70%) for all")
print()

phishing_patterns = [
    ("https://paypal-verify-account.tk", "Suspicious TLD + keywords"),
    ("https://google-login-secure.ml", "Brand + suspicious TLD"),
    ("http://185.220.101.12/login", "IP address"),
    ("https://secure-facebook-verify.ga", "Brand + keywords + TLD"),
    ("https://instagram-security-check.cf", "Brand + keywords + TLD"),
    ("https://amazon-prime-renewal.gq", "Brand + keywords + TLD"),
    ("https://microsoft-account-verify.tk", "Brand + keywords + TLD"),
    ("https://apple-icloud-unlock.ml", "Brand + keywords + TLD"),
]

test2_passed = 0
test2_total = len(phishing_patterns)

for url, description in phishing_patterns:
    feats = extractor.extract(url)
    df = pd.DataFrame([feats])
    df = df.reindex(columns=feature_names, fill_value=0)
    
    prob = model.predict_proba(df)[0][1]
    risk_pct = prob * 100
    
    if risk_pct > 70:
        status = "✅ PASS"
        test2_passed += 1
    else:
        status = "❌ FAIL (Too low risk)"
    
    print(f"{status:20} {risk_pct:5.1f}% - {description:30} {url}")

print(f"\nTest 2 Result: {test2_passed}/{test2_total} passed ({test2_passed/test2_total*100:.0f}%)")

# ============================================================
# TEST SET 3: Edge Cases
# ============================================================
print("\n" + "="*70)
print(" TEST 3: EDGE CASES")
print("="*70)
print("Testing borderline URLs")
print()

edge_cases = [
    ("https://www.ihecs.be", "Obscure but legitimate", "SAFE"),
    ("https://secure-login-portal.com", "Generic suspicious", "PHISHING"),
    ("https://verify-account-now.net", "Suspicious keywords", "PHISHING"),
    ("https://www.bbc.co.uk/news", "Legitimate news", "SAFE"),
]

test3_passed = 0
test3_total = len(edge_cases)

for url, description, expected in edge_cases:
    feats = extractor.extract(url)
    df = pd.DataFrame([feats])
    df = df.reindex(columns=feature_names, fill_value=0)
    
    prob = model.predict_proba(df)[0][1]
    risk_pct = prob * 100
    
    # Check if whitelisted
    domain = url.lower().replace("https://", "").replace("http://", "").split("/")[0]
    is_whitelisted = extractor.is_legitimate_domain(domain)
    
    if is_whitelisted:
        prediction = "SAFE (Whitelisted)"
    elif risk_pct > 50:
        prediction = "PHISHING"
    else:
        prediction = "SAFE"
    
    if expected in prediction:
        status = "✅ PASS"
        test3_passed += 1
    else:
        status = "❌ FAIL"
    
    print(f"{status:20} {risk_pct:5.1f}% - {description:25} Expected: {expected:10} Got: {prediction}")

print(f"\nTest 3 Result: {test3_passed}/{test3_total} passed ({test3_passed/test3_total*100:.0f}%)")

# ============================================================
# OVERALL SUMMARY
# ============================================================
print("\n" + "="*70)
print(" 📊 OVERALL VALIDATION SUMMARY")
print("="*70)

total_passed = test1_passed + test2_passed + test3_passed
total_tests = test1_total + test2_total + test3_total
overall_accuracy = total_passed / total_tests * 100

print(f"\nTest 1 (Unseen Legitimate):  {test1_passed}/{test1_total} ({test1_passed/test1_total*100:.0f}%)")
print(f"Test 2 (Phishing Patterns):  {test2_passed}/{test2_total} ({test2_passed/test2_total*100:.0f}%)")
print(f"Test 3 (Edge Cases):         {test3_passed}/{test3_total} ({test3_passed/test3_total*100:.0f}%)")
print(f"\n{'='*70}")
print(f"OVERALL: {total_passed}/{total_tests} ({overall_accuracy:.1f}%)")
print("="*70)

if overall_accuracy >= 85:
    print("\n✅ EXCELLENT - Model successfully learned patterns!")
    print("   The model can generalize to unseen URLs.")
elif overall_accuracy >= 70:
    print("\n⚠️  GOOD - Model shows pattern learning but needs improvement")
    print("   Consider adjusting regularization parameters.")
else:
    print("\n❌ POOR - Model still overfitting or underfitting")
    print("   Recommended actions:")
    print("   1. Check if training completed successfully")
    print("   2. Review training metrics")
    print("   3. Consider adjusting regularization parameters")

print("\n" + "="*70 + "\n")
