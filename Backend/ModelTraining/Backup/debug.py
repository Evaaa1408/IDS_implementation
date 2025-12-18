import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from Data_Preprocessing.feature_extractor import URLFeatureExtractor

print("="*70)
print(" 🔍 DEBUGGING: Why g00gle.com is not detected")
print("="*70)

extractor = URLFeatureExtractor()

# Test URLs
test_urls = [
    "https://www.google.com",
    "https://www.g00gle.com",
    "https://www.gooogle.com",
]

for url in test_urls:
    print(f"\n📝 Testing: {url}")
    features = extractor.extract(url)
    
    # Check advanced features
    advanced = [
        'CharacterSubstitutions',
        'TyposquattingScore',
        'KnownTyposquatting',
        'Combosquatting',
        'SuspiciousTLD'
    ]
    
    print(f"   Advanced Features:")
    for feat in advanced:
        value = features[feat]
        if value > 0:
            print(f"      🚨 {feat}: {value}")
        else:
            print(f"      ✅ {feat}: {value}")
    
    # Check if it's considered legitimate
    import tldextract
    ext = tldextract.extract(url)
    domain_with_tld = f"{ext.domain}.{ext.suffix}"
    
    is_legit = extractor.is_legitimate_domain(domain_with_tld)
    print(f"   Is Legitimate: {is_legit}")
    print(f"   Domain: {domain_with_tld}")

print("\n" + "="*70)
print(" 💡 DIAGNOSIS")
print("="*70)
print("""
If g00gle.com shows:
  - Is Legitimate: False
  - CharacterSubstitutions: 2 (because of two '0's)
  - TyposquattingScore: 0-2

Then the feature extractor is working correctly, but the MODEL
didn't learn that these features = phishing.

SOLUTION: The model needs more training examples of typosquatting!
""")
print("="*70)