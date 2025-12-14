
import sys
import os
import pandas as pd
import joblib

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Data_Preprocessing.feature_extractor import URLFeatureExtractor

def debug_url(url):
    print(f"\n🔍 DEBUGGING URL: {url}")
    print("="*60)
    
    # 1. Load Model and Features
    try:
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Models/2025/model_2025.pkl'))
        feats_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Models/2025/features_2025.pkl'))
        
        model = joblib.load(model_path)
        feature_names = joblib.load(feats_path)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    # 2. Extract Features
    extractor = URLFeatureExtractor()
    features = extractor.extract(url)
    
    # 3. Create DataFrame
    df = pd.DataFrame([features])
    df = df.reindex(columns=feature_names, fill_value=0)
    
    # 4. Predict
    prob = model.predict_proba(df)[0][1]
    print(f"\n💰 PREDICTED HIGH RISK: {prob*100:.4f}%")
    
    # 5. Analyze Top Features
    print("\n📊 Feature Analysis (Top contributors?):")
    # This is a random forest/GBM likely, so we can't easily get 'contribution' per instance without SHAP
    # But we can look at the feature values themselves
    
    pd.set_option('display.max_rows', None)
    # Transpose for easier reading
    print(df.T)

if __name__ == "__main__":
    debug_url("https://www.instagram.com")
    debug_url("https://instagram.com")
