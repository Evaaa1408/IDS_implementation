import joblib
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Data_Preprocessing.feature_extract_2023 import ContentFeatureExtractor
from Data_Preprocessing.feature_extractor import URLFeatureExtractor

class EnsemblePredictor:
    def __init__(self):
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        self.models_path = os.path.join(self.base_path, 'Models')
        
        # ========================================================
        # SMART WEIGHTING STRATEGY
        # ========================================================
        # Model 2025 (URL-based) is more reliable in testing
        # Give it 70% weight, Model 2023 gets 30%
        self.WEIGHT_2025 = 0.7
        self.WEIGHT_2023 = 0.3
        
        # Adjusted threshold to reduce false positives
        self.THRESHOLD = 0.65  # Only block if 65%+ confident
        
        print("Loading Ensemble Models...")
        try:
            # Load Model 2025 (URL)
            self.model_2025 = joblib.load(os.path.join(self.models_path, '2025/model_2025.pkl'))
            self.feats_2025 = joblib.load(os.path.join(self.models_path, '2025/features_2025.pkl'))
            self.extractor_2025 = URLFeatureExtractor()
            print("✅ Model 2025 Loaded")

            # Load Model 2023 (Content)
            self.model_2023 = joblib.load(os.path.join(self.models_path, '2023/model_2023.pkl'))
            self.feats_2023 = joblib.load(os.path.join(self.models_path, '2023/features_2023.pkl'))
            self.extractor_2023 = ContentFeatureExtractor()
            print("✅ Model 2023 Loaded")

            # Load Meta-Model (optional)
            meta_path = os.path.join(self.models_path, 'Ensemble/meta_model.pkl')
            if os.path.exists(meta_path):
                self.meta_model = joblib.load(meta_path)
                self.has_meta = True
                print("✅ Meta-Model Loaded")
            else:
                self.has_meta = False
                print("⚠️ Meta-Model not found. Using Weighted Average Strategy.")

        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise e

    def predict(self, url, html_content=None):
        """
        Smart Ensemble Prediction with Weighted Voting and Confidence Analysis
        """
        results = {}

        # =================================================================
        # 1. MODEL 2025 PREDICTION (URL-based) - PRIMARY MODEL
        # =================================================================
        try:
            feats_url = self.extractor_2025.extract(url)
            
            df_25 = pd.DataFrame([feats_url])
            df_25 = df_25.reindex(columns=self.feats_2025, fill_value=0)
            
            proba_2025 = self.model_2025.predict_proba(df_25)[0]
            prob_legit_2025 = proba_2025[1] 
            prob_phish_2025 = proba_2025[0] 
            
            print(f"DEBUG Model 2025: Legit={prob_legit_2025:.4f}, Phish={prob_phish_2025:.4f}")
            
            results['prob_2025'] = float(prob_phish_2025)
            
        except Exception as e:
            print(f"Error in Model 2025: {e}")
            import traceback
            traceback.print_exc()
            results['prob_2025'] = 0.5

        # =================================================================
        # 2. MODEL 2023 PREDICTION (Content-based)
        # =================================================================
        if html_content:
            try:
                feats_content = self.extractor_2023.extract_from_html(html_content, url)
                
                df_23 = pd.DataFrame([feats_content])
                df_23 = df_23.reindex(columns=self.feats_2023, fill_value=0)
                
                proba_2023 = self.model_2023.predict_proba(df_23)[0]
                prob_legit_2023 = proba_2023[0]
                prob_phish_2023 = proba_2023[1]
                
                print(f"DEBUG Model 2023: Legit={prob_legit_2023:.4f}, Phish={prob_phish_2023:.4f}")
                
                results['prob_2023'] = float(prob_phish_2023)
                
                # Check HTML quality
                html_quality = self._assess_html_quality(feats_content)
                results['html_quality'] = html_quality
                
            except Exception as e:
                print(f"Error in Model 2023: {e}")
                import traceback
                traceback.print_exc()
                results['prob_2023'] = None
                results['html_quality'] = 'error'
        else:
            results['prob_2023'] = None
            results['html_quality'] = 'none'

        # =================================================================
        # 3. SMART ENSEMBLE DECISION
        # =================================================================
        final_prob = self._calculate_ensemble_probability(results)
        
        results['final_probability'] = float(final_prob)
        results['is_phishing'] = bool(final_prob > self.THRESHOLD)
        results['threshold_used'] = self.THRESHOLD
        results['decision_logic'] = self._get_decision_logic(results)

        # =================================================================
        # DEBUG OUTPUT
        # =================================================================
        print("\n" + "="*70)
        print(f"FINAL RESULT: {url}")
        print("="*70)
        print(f"  Model 2025 (URL):    {results['prob_2025']:.4f} (Weight: {self.WEIGHT_2025})")
        if results['prob_2023'] is not None:
            print(f"  Model 2023 (Content): {results['prob_2023']:.4f} (Weight: {self.WEIGHT_2023})")
            print(f"  HTML Quality:        {results['html_quality']}")
        else:
            print(f"  Model 2023 (Content): N/A (No HTML provided)")
        print(f"  Final Probability:   {results['final_probability']:.4f}")
        print(f"  Threshold:           {self.THRESHOLD}")
        print(f"  Decision:            {'🚨 BLOCK' if results['is_phishing'] else '✅ ALLOW'}")
        print(f"  Logic:               {results['decision_logic']}")
        print("="*70 + "\n")

        return results

    def _assess_html_quality(self, features):
        """
        Assess if HTML content is realistic enough for Model 2023
        Returns: 'good', 'poor', or 'minimal'
        """
        # Check if HTML has meaningful content
        has_images = features.get('NoOfImage', 0) > 0
        has_css = features.get('NoOfCSS', 0) > 0
        has_js = features.get('NoOfJS', 0) > 0
        line_count = features.get('LineOfCode', 0)
        
        meaningful_features = sum([has_images, has_css, has_js])
        
        if meaningful_features >= 2 and line_count > 50:
            return 'good'
        elif meaningful_features >= 1 or line_count > 20:
            return 'poor'
        else:
            return 'minimal'

    def _calculate_ensemble_probability(self, results):
        """
        Smart ensemble calculation with multiple strategies
        """
        prob_2025 = results['prob_2025']
        prob_2023 = results.get('prob_2023')
        html_quality = results.get('html_quality', 'none')
        
        # ========================================================
        # STRATEGY 1: URL-Only Mode (No HTML)
        # ========================================================
        if prob_2023 is None:
            # Use only Model 2025, but apply subdomain correction
            return self._apply_subdomain_correction(prob_2025, results)
        
        # ========================================================
        # STRATEGY 2: High Agreement (Both models agree)
        # ========================================================
        if abs(prob_2025 - prob_2023) < 0.3:
            # Models agree - use simple weighted average
            if self.has_meta:
                meta_input = pd.DataFrame([{
                    'prob_2023': prob_2023,
                    'prob_2025': prob_2025
                }])
                return self.meta_model.predict_proba(meta_input)[0][1]
            else:
                return (self.WEIGHT_2025 * prob_2025) + (self.WEIGHT_2023 * prob_2023)
        
        # ========================================================
        # STRATEGY 3: Disagreement - Trust the more reliable model
        # ========================================================
        
        # If HTML is minimal/poor, trust Model 2025 more
        if html_quality in ['minimal', 'poor']:
            # Give Model 2025 even more weight (85%)
            return 0.85 * prob_2025 + 0.15 * prob_2023
        
        # If Model 2025 says safe but Model 2023 says phishing
        # (Common false positive pattern from test results)
        if prob_2025 < 0.3 and prob_2023 > 0.7:
            # Strongly trust Model 2025 (90% weight)
            return 0.9 * prob_2025 + 0.1 * prob_2023
        
        # If Model 2025 says phishing but Model 2023 says safe
        if prob_2025 > 0.7 and prob_2023 < 0.3:
            # Both models contribute, but favor Model 2025
            return 0.75 * prob_2025 + 0.25 * prob_2023
        
        # Default: Use standard weights
        return (self.WEIGHT_2025 * prob_2025) + (self.WEIGHT_2023 * prob_2023)

    def _apply_subdomain_correction(self, prob, results):
        """
        Correct for subdomain bias in Model 2025
        """
        # This is a temporary fix until you retrain Model 2025
        # If probability is high but only because of missing 'www'
        
        # You can add logic here to detect if the URL is from a known legitimate domain
        # For now, we return the probability as-is
        # You could implement a whitelist of known-safe domains without www
        
        return prob

    def _get_decision_logic(self, results):
        """
        Explain which strategy was used for transparency
        """
        prob_2025 = results['prob_2025']
        prob_2023 = results.get('prob_2023')
        html_quality = results.get('html_quality', 'none')
        
        if prob_2023 is None:
            return "URL-only mode (Model 2025)"
        
        if abs(prob_2025 - prob_2023) < 0.3:
            return "High agreement - weighted average"
        
        if html_quality in ['minimal', 'poor']:
            return f"Poor HTML quality ({html_quality}) - trust URL model (85%)"
        
        if prob_2025 < 0.3 and prob_2023 > 0.7:
            return "Model disagreement - trust URL model (90%)"
        
        if prob_2025 > 0.7 and prob_2023 < 0.3:
            return "Model disagreement - favor URL model (75%)"
        
        return "Standard weighted ensemble (70/30)"

if __name__ == "__main__":
    predictor = EnsemblePredictor()
    
    print("\n🧪 COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    test_cases = [
        {
            "url": "https://www.google.com",
            "html": "<html><head><title>Google</title><link rel='stylesheet' href='style.css'><script src='app.js'></script></head><body><img src='logo.png'/><form><input type='text'/></form></body></html>",
            "expected": "Safe",
            "description": "Major search engine with realistic HTML"
        },
        {
            "url": "https://www.facebook.com",
            "html": None,
            "expected": "Safe",
            "description": "Social media - URL-only mode"
        },
        {
            "url": "http://secure-login-verify-account.com/update.php",
            "html": "<html><body><form action='http://evil.com'><input type='password'/><input type='hidden'/></form></body></html>",
            "expected": "Phishing",
            "description": "Suspicious URL with phishing form"
        },
        {
            "url": "https://www.github.com",
            "html": "<html><head><title>GitHub</title></head><body><p>Code hosting</p></body></html>",
            "expected": "Safe",
            "description": "Developer platform with minimal HTML"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test['description']}")
        print(f"Expected: {test['expected']}")
        print(f"{'='*70}")
        
        result = predictor.predict(test['url'], test['html'])
        
        actual = "Phishing" if result['is_phishing'] else "Safe"
        status = "✅ PASS" if actual == test['expected'] else "❌ FAIL"
        
        print(f"\n{status} - Predicted: {actual}, Expected: {test['expected']}")
        print(f"Confidence: {result['final_probability']:.2%}")
        print(f"Logic Used: {result['decision_logic']}")