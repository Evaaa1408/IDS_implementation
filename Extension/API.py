#API.py
import pandas as pd
import threading
import subprocess
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))
from Ensemble_Predict import EnsemblePredictor
from DataCollector import DataCollector

app = Flask(__name__)
# Enable CORS for all routes (Chrome Extension + Dashboard)
CORS(app) 

# -------------------------------------------------------------------
# DASHBOARD SERVING
# -------------------------------------------------------------------
@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Serves the Admin Dashboard HTML"""
    dashboard_path = os.path.join(os.path.dirname(__file__), '../../Frontend/dashboard.html')
    if os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return "Dashboard file not found!", 404

@app.route("/dashboard.css", methods=["GET"])
def dashboard_css():
    """Serves the Dashboard CSS"""
    css_path = os.path.join(os.path.dirname(__file__), '../../Frontend/dashboard.css')
    if os.path.exists(css_path):
        return send_file(css_path)
    return "CSS file not found!", 404

@app.route("/dashboard.js", methods=["GET"])
def dashboard_js():
    """Serves the Dashboard JS"""
    js_path = os.path.join(os.path.dirname(__file__), '../../Frontend/dashboard.js')
    if os.path.exists(js_path):
        return send_file(js_path)
    return "JS file not found!", 404

# -------------------------------------------------------------------
# ADMIN ENDPOINTS (Logs, Verify, Retrain)
# -------------------------------------------------------------------

@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Returns the self-learning data as JSON"""
    if not collector:
        return jsonify([])
    
    csv_path = collector.log_file
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # Replace NaN with null for JSON compatibility
            df = df.where(pd.notnull(df), None)
            return jsonify(df.to_dict(orient="records"))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify([])

@app.route("/api/verify", methods=["POST"])
def verify_log():
    """Moves a log entry: Safe (Keep but mark) OR Remove (Delete)"""
    data = request.get_json()
    log_id = data.get("id")
    action = data.get("action") # 'safe' or 'remove'
    
    if not collector or not log_id:
        return jsonify({"error": "Invalid request"}), 400

    csv_path = collector.log_file
    if not os.path.exists(csv_path):
        return jsonify({"error": "No logs found"}), 404

    try:
        df = pd.read_csv(csv_path)
        
        if action == "remove":
            # Delete row
            df = df[df["id"] != log_id]
            msg = "Log entry removed."
        elif action == "safe":
            # Mark as not phishing (False Positive fix)
            df.loc[df["id"] == log_id, "is_phishing"] = False
            msg = "Marked as Safe."
        else:
            return jsonify({"error": "Unknown action"}), 400
            
        df.to_csv(csv_path, index=False)
        return jsonify({"message": msg})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/retrain", methods=["POST"])
def trigger_retrain():
    """Triggers the backend retraining script in a background thread"""
    data = request.get_json()
    period = data.get("period", "manual")
    
    def run_training():
        print(f"🔥 [Background] Retraining started (Period: {period})...")
        try:
            # Path to Train Script
            script_path = os.path.join(os.path.dirname(__file__), "../../Backend/ModelTraining/Train_2023_Refined.py")
            result = subprocess.run(["python", script_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ [Background] Retraining SUCCESS!")
            else:
                print(f"❌ [Background] Retraining FAILED: {result.stderr}")
        except Exception as e:
            print(f"❌ [Background] Error: {e}")

    # Start thread
    thread = threading.Thread(target=run_training)
    thread.daemon = True # Detached thread
    thread.start()
    
    return jsonify({"message": "Training started in background! Check console for progress."}) 

# Initialize Predictor
try:
    predictor = EnsemblePredictor()
    print("✅ Ensemble Predictor Initialized")
except Exception as e:
    print(f"❌ Failed to initialize predictor: {e}")
    predictor = None

# Initialize DataCollector (Self-Learning)
try:
    collector = DataCollector()
    print("✅ DataCollector Initialized")
except Exception as e:
    print(f"❌ Failed to initialize collector: {e}")
    collector = None

# log_phishing_attempt removed in favor of DataCollector

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running", 
        "model": "Ensemble (Model 2023 + Model 2025)",
        "framework": "Flask"
    })

@app.route("/predict", methods=["POST"])
def predict():
    if not predictor:
        return jsonify({"error": "Model not initialized"}), 500
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    url = data['url']
    html_content = data.get('html_content') # Optional
    
    try:
        # Run prediction
        result = predictor.predict(url, html_content)
        
        # Log data for Self-Learning (if collector is active)
        if collector:
            try:
                # Log usage data (Self-Learning Loop)
                req_id = collector.log_result(url, result, html_content)
                result['request_id'] = req_id
            except Exception as e_log:
                print(f"⚠️ logging warning: {e_log}")
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run on host 0.0.0.0 to listen on all interfaces, but strictly local use 127.0.0.1 is fine too.
    # Port 5000 is standard for Flask.
    print("🚀 Starting Flask API on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
