import sys
import os

# Add Backend path
sys.path.append(os.path.abspath("Backend/Ensemble"))

from Ensemble_Predict import EnsemblePredictor

def test():
    print("Initializing EnsemblePredictor...")
    try:
        predictor = EnsemblePredictor()
    except Exception as e:
        print(f"FAILED to initialize: {e}")
        return

    test_url = "https://google.com"
    print(f"\nTesting URL: {test_url}")
    
    # 1. Test URL Only (Model 2025)
    result = predictor.predict(test_url, html_content=None)
    print("Result (URL Only):", result)
    
if __name__ == "__main__":
    test()
