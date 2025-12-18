# test_model_2025_live.py
import sys
sys.path.append('.')
from Data_Preprocessing.feature_extractor import URLFeatureExtractor
import pandas as pd
import joblib

extractor = URLFeatureExtractor()
model = joblib.load('Models/2025/model_2025.pkl')
features = joblib.load('Models/2025/features_2025.pkl')

# Test YouTube
url = "https://www.youtube.com"
feats = extractor.extract(url)
df = pd.DataFrame([feats]).reindex(columns=features, fill_value=0)
prob = model.predict_proba(df)[0]

print(f"YouTube Phishing Prob: {prob[1]:.4f}")
print(f"Expected: < 0.01")
print(f"Whitelist Check: {extractor.is_legitimate_domain('youtube.com')}")

if prob[1] > 0.5:
    print("❌ FAILED! Model 2025 needs retraining!")
    print("\nFIX:")
    print("1. Verify whitelist in feature_extractor.py")
    print("2. python Data_Preprocessing/feature_extract_2025.py")
    print("3. python Backend/ModelTraining/Train_2025.py")
