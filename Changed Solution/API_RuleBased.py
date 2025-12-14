from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys

sys.path.append(os.path.dirname(__file__))

from Ensemble_Rulebased import RuleBasedFusionPredictor

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome Extension

# Initialize Predictor
try:
    predictor = RuleBasedFusionPredictor()
    print("✅ Rule-Based Predictor Initialized")
except Exception as e:
    print(f"❌ Failed to initialize predictor: {e}")
    predictor = None

# -------------------------------------------------------------------
# MAIN ENDPOINTS
# -------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running", 
        "model": "Rule-Based Fusion (Model 2023 + Model 2025)",
        "framework": "Flask",
        "method": "No Ensemble Training - Pure Logic Rules"
    })

@app.route("/predict", methods=["POST"])
def predict():
    if not predictor:
        return jsonify({"error": "Model not initialized"}), 500
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    url = data['url']
    html_content = data.get('html_content')  # Optional
    html_captured = data.get('html_captured', False)
    
    try:
        # Log request
        print(f"\n{'='*70}")
        print(f"📡 API REQUEST")
        print(f"{'='*70}")
        print(f"URL: {url}")
        print(f"HTML Available: {html_content is not None}")
        print(f"HTML Captured Flag: {html_captured}")
        
        # Run prediction
        result = predictor.predict(url, html_content)
        
        # Format response for browser extension
        response = {
            # Input info
            "url": url,
            "html_available": result.get('html_available', False),
            
            # Model predictions
            "url_prob": result.get('url_prob', 0.0),
            "content_prob": result.get('content_prob', 0.0),
            
            # Final decision
            "final_risk_pct": result.get('final_risk_pct', 0.0),
            "risk_level": result.get('risk_level', 'UNKNOWN'),
            "color": result.get('color', 'gray'),
            "confidence": result.get('confidence', 'UNKNOWN'),
            "is_phishing": result.get('is_phishing', False),
            "message": result.get('message', ''),
            
            # Additional info
            "whitelisted": result.get('whitelisted', False),
            "method": result.get('method', 'Rule-Based Fusion')
        }
        
        # Log response
        print(f"\n📤 API RESPONSE")
        print(f"{'='*70}")
        print(f"Risk Level: {response['risk_level']}")
        print(f"Final Risk: {response['final_risk_pct']:.1f}%")
        print(f"Color: {response['color']}")
        print(f"Is Phishing: {response['is_phishing']}")
        print(f"{'='*70}\n")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# OPTIONAL: Dashboard Endpoints (You can keep or remove these)
# -------------------------------------------------------------------

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Serves the Admin Dashboard HTML"""
    dashboard_path = os.path.join(os.path.dirname(__file__), '../Frontend/dashboard.html')
    if os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return "Dashboard not available - file not found", 404

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Simple stats endpoint (OPTIONAL)
    Can be used to show system status in dashboard
    """
    if not predictor:
        return jsonify({"error": "Predictor not initialized"}), 500
    
    return jsonify({
        "status": "running",
        "predictor_type": "Rule-Based Fusion",
        "model_2025_inverted": getattr(predictor, 'MODEL_2025_INVERTED', False),
        "model_2023_inverted": getattr(predictor, 'MODEL_2023_INVERTED', False),
        "whitelist_size": len(getattr(predictor, 'legitimate_brands', [])),
        "method": "Independent Models + Logic Rules"
    })

# -------------------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "predictor": "active" if predictor else "inactive"
    })

if __name__ == "__main__":
    print("="*70)
    print(" 🚀 STARTING RULE-BASED PHISHING DETECTION API")
    print("="*70)
    print("\n📋 Configuration:")
    print("   • Method: Rule-Based Fusion")
    print("   • Port: 5000")
    print("   • CORS: Enabled")
    print("   • DataCollector: Disabled (removed)")
    print("\n🌐 Endpoints:")
    print("   • POST /predict - Main prediction")
    print("   • GET /health - Health check")
    print("   • GET /api/stats - System stats")
    print("\n" + "="*70 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=True)        