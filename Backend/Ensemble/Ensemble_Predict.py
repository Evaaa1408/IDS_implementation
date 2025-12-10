import joblib
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path to find Data_Preprocessing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Data_Preprocessing.feature_extract_2023 import ContentFeatureExtractor
from Data_Preprocessing.feature_extractor import URLFeatureExtractor

class EnsemblePredictor:
    def __init__(self):
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        self.models_path = os.path.join(self.base_path, 'Models')
        
        print("Loading Ensemble Models...")
        try:
            # Load Model 2025 (URL)
            self.model_2025 = joblib.load(os.path.join(self.models_path, '2025/model_2025.pkl'))
            self.feats_2025 = joblib.load(os.path.join(self.models_path, '2025/features_2025.pkl'))
            
            # DEBUG: Log features to file
            with open("debug_features.txt", "w") as f:
                f.write(str(self.feats_2025))
            
            self.extractor_2025 = URLFeatureExtractor()
            print("✅ Model 2025 Loaded")

            # Load Model 2023 (Content)
            self.model_2023 = joblib.load(os.path.join(self.models_path, '2023/model_2023.pkl'))
            self.feats_2023 = joblib.load(os.path.join(self.models_path, '2023/features_2023.pkl'))
            self.extractor_2023 = ContentFeatureExtractor()
            print("✅ Model 2023 Loaded")

            # Load Meta-Model
            # Note: If meta_model doesn't exist yet, we can use a simple average fallback
            meta_path = os.path.join(self.models_path, 'Ensemble/meta_model.pkl')
            if os.path.exists(meta_path):
                self.meta_model = joblib.load(meta_path)
                self.has_meta = True
                print("✅ Meta-Model Loaded")
            else:
                self.has_meta = False
                print("⚠️ Meta-Model not found. Using Average Strategy.")

        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise e

    def predict(self, url, html_content=None):
        """
        Main prediction function.
        If html_content is provided, runs full ensemble.
        If not, runs only Model 2025 (Fast Scan).
        """
        results = {}

        # 1. Fast Scan (Model 2025)
        try:
            feats_url = self.extractor_2025.extract(url)
            
            df_25 = pd.DataFrame([feats_url])
            # Align columns
            df_25 = df_25.reindex(columns=self.feats_2025, fill_value=0)
            
            # [Standardized] Model 2025: 1=Phishing, 0=Legitimate
            
            prob_2025 = self.model_2025.predict_proba(df_25)[0][1]
            
            results['prob_2025'] = float(prob_2025)
        except Exception as e:
            print(f"Error in Model 2025: {e}")
            results['prob_2025'] = 0.5 # Uncertainty
        if html_content:
            try:
                # Use the new offline extraction method
                feats_content = self.extractor_2023.extract_from_html(html_content, url)
                
                df_23 = pd.DataFrame([feats_content])
                df_23 = df_23.reindex(columns=self.feats_2023, fill_value=0)
                
                # [Standardized] Model 2023 labels: 1=Phishing, 0=Legitimate
                # We take index [1] to get the Phishing Probability
                prob_2023 = self.model_2023.predict_proba(df_23)[0][1]
                results['prob_2023'] = float(prob_2023)
                
            except Exception as e:
                print(f"Error in Model 2023: {e}")
                results['prob_2023'] = 0.5

            # 3. Ensemble Verdict
            if self.has_meta:
                meta_input = pd.DataFrame([{
                    'prob_2023': results['prob_2023'],
                    'prob_2025': results['prob_2025']
                }])
                final_prob = self.meta_model.predict_proba(meta_input)[0][1]
            else:
                # Fallback Strategy: Average
                final_prob = (results['prob_2023'] + results['prob_2025']) / 2
            
            results['final_probability'] = float(final_prob)
            results['is_phishing'] = bool(final_prob > 0.5)
            
        else:
            # URL Only mode
            results['final_probability'] = results['prob_2025']
            results['is_phishing'] = bool(results['prob_2025'] > 0.5)
            results['note'] = "Fast Scan Only (URL)"

        return results

if __name__ == "__main__":
    # Test
    predictor = EnsemblePredictor()
    print(predictor.predict("http://centralassociatesltd.com/richieeee/index.php", html_content="<html>...</html>"))
