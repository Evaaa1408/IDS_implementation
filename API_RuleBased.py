#API_RuleBased.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import csv
import json
from datetime import datetime
import tldextract

sys.path.append(os.path.dirname(__file__))

from RuleBased.Ensemble_Rulebased import RuleBasedFusionPredictor

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome Extension

# Initialize Predictor
try:
    predictor = RuleBasedFusionPredictor()
    print("✅ Rule-Based Predictor Initialized")
except Exception as e:
    print(f"❌ Failed to initialize predictor: {e}")
    predictor = None

# File paths
LOG_FILE = os.path.join(os.path.dirname(__file__), 'HTML_logs', 'Malicious_log.csv')
FALSE_POSITIVE_FILE = os.path.join(os.path.dirname(__file__), 'HTML_logs', 'false_positive_log.json')

# Initialize CSV file if it doesn't exist
if not os.path.exists(LOG_FILE):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'url', 'domain', 'prediction', 'probability', 'action', 'risk_level', 'reason', 'detailed_reason'])

# Initialize false positive file
if not os.path.exists(FALSE_POSITIVE_FILE):
    with open(FALSE_POSITIVE_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def get_risk_level(probability):
    """Determine risk level based on probability"""
    prob = float(probability.replace('%', '')) if isinstance(probability, str) else probability
    if prob >= 75:
        return '🔴 High'
    elif prob >= 55:
        return '🟠 Medium'
    elif prob >= 40:
        return '🟡 Low'
    else:
        return '✅ Safe'

def extract_feature_explanations(url, result):
    """Extract detailed reasons why URL was flagged"""
    explanations = []
    
    # URL-based features
    if result.get('url_prob', 0) > 0.5:
        url_features = result.get('url_features', {})
        
        # Check for specific suspicious patterns
        if url_features.get('url_entropy', 0) > 0.7:
            explanations.append(f"High URL entropy (+{url_features.get('url_entropy', 0):.2f})")
        
        if url_features.get('NumberLetterMixing', 0) == 1:
            explanations.append("Number-letter mixing detected")
        
        if url_features.get('SuspiciousTLD', 0) == 1:
            explanations.append("Suspicious TLD detected")
        
        if url_features.get('TyposquattingScore', 0) > 5:
            score = url_features.get('TyposquattingScore', 0)
            explanations.append(f"Typosquatting score: {score:.1f} / 10")
        
        if url_features.get('is_slug_like', 0) == 0 and '/' in url:
            explanations.append("No readable slug detected")
        
        if url_features.get('ExcessiveHyphens', 0) == 1:
            explanations.append("Excessive hyphens in domain")
        
        if url_features.get('Combosquatting', 0) > 0:
            explanations.append("Combosquatting pattern detected")
    
    # Content-based features
    if result.get('content_prob', 0) > 0.5:
        explanations.append("Suspicious page content detected")
    
    # Add risk level info
    risk_pct = result.get('final_risk_pct', 0)
    explanations.append(f"Overall risk probability: {risk_pct:.1f}%")
    
    return explanations

def log_to_csv(url, result):
    "Log phishing to CSV file"
    try:
        # Extract domain
        ext = tldextract.extract(url)
        domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
        
        # Determine action based on risk level
        risk_level_text = result.get('risk_level', 'UNKNOWN')
        if risk_level_text == 'VERY SUSPICIOUS':
            action = 'Blocked'
        elif risk_level_text == 'POSSIBLY MALICIOUS':
            action = 'Warned'
        else:
            action = 'Allowed'
        
        # Only log threats!
        if action == 'Allowed':
            return 
        # Get prediction
        is_phishing = result.get('is_phishing', False)
        prediction = 'Phishing' if is_phishing else 'Legitimate'
        
        # Get probability
        probability = result.get('final_risk_pct', 0.0)
        prob_str = f"{probability:.2f}%"
        
        # Get risk level indicator
        risk_indicator = get_risk_level(probability)
        
        # Build simple reason
        reasons = []
        if result.get('url_prob', 0) > 0.5:
            reasons.append('Suspicious URL pattern')
        if result.get('content_prob', 0) > 0.5:
            reasons.append('Suspicious content')
        if result.get('whitelisted'):
            reasons.append('Whitelisted domain')
        
        reason = ', '.join(reasons) if reasons else result.get('risk_level', 'Unknown')
        
        # Get detailed explanations
        detailed_explanations = extract_feature_explanations(url, result)
        detailed_reason = ' • ' + '\n• '.join(detailed_explanations) if detailed_explanations else reason
        
        # Write to CSV - blocked and Warned URLs
        with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                url,
                domain,
                prediction,
                prob_str,
                action,
                risk_indicator,
                reason,
                detailed_reason
            ])
    except Exception as e:
        print(f"⚠️ Error logging to CSV: {e}")

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
        
        # Log to CSV if phishing detected or warned
        if response['is_phishing']:
            log_to_csv(url, result)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# Dashboard Endpoints
# -------------------------------------------------------------------

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Serves the Admin Dashboard HTML"""
    dashboard_path = os.path.join(os.path.dirname(__file__), 'Frontend', 'dashboard.html')
    if os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return "Dashboard not available - file not found", 404

@app.route("/dashboard.css", methods=["GET"])
def dashboard_css():
    """Serves the Dashboard CSS"""
    css_path = os.path.join(os.path.dirname(__file__), 'Frontend', 'dashboard.css')
    if os.path.exists(css_path):
        return send_file(css_path, mimetype='text/css')
    return "CSS not found", 404

@app.route("/dashboard.js", methods=["GET"])
def dashboard_js():
    """Serves the Dashboard JavaScript"""
    js_path = os.path.join(os.path.dirname(__file__), 'Frontend', 'dashboard.js')
    if os.path.exists(js_path):
        return send_file(js_path, mimetype='application/javascript')
    return "JS not found", 404

@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Get phishing log data for dashboard"""
    try:
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    logs.append(row)
        
        # Return in reverse order (newest first)
        logs.reverse()
        return jsonify({
            "success": True,
            "logs": logs,
            "total": len(logs)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get dashboard statistics including today's summary"""
    try:
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    logs.append(row)
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Calculate stats
        total = len(logs)
        today_logs = [log for log in logs if log['timestamp'].startswith(today)]
        
        blocked_total = len([log for log in logs if log['action'] == 'Blocked'])
        warned_total = len([log for log in logs if log['action'] == 'Warned'])
        
        blocked_today = len([log for log in today_logs if log['action'] == 'Blocked'])
        warned_today = len([log for log in today_logs if log['action'] == 'Warned'])
        
        # Get false positives
        false_positives = []
        if os.path.exists(FALSE_POSITIVE_FILE):
            with open(FALSE_POSITIVE_FILE, 'r', encoding='utf-8') as f:
                false_positives = json.load(f)
        
        false_positive_count = len(false_positives)
        false_positive_today = len([fp for fp in false_positives if fp.get('marked_at', '').startswith(today)])
        
        return jsonify({
            "success": True,
            "total_detections": total,
            "blocked_total": blocked_total,
            "warned_total": warned_total,
            "today_total": len(today_logs),
            "today_blocked": blocked_today,
            "today_warned": warned_today,
            "false_positives_total": false_positive_count,
            "false_positives_today": false_positive_today
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/false_positives", methods=["GET"])
def get_false_positives():
    """Get list of reported false positives for dashboard"""
    try:
        false_positives = []
        if os.path.exists(FALSE_POSITIVE_FILE):
            with open(FALSE_POSITIVE_FILE, 'r', encoding='utf-8') as f:
                false_positives = json.load(f)
        
        # Return in reverse order (newest first)
        false_positives.reverse()
        return jsonify({
            "success": True,
            "false_positives": false_positives,
            "total": len(false_positives)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/mark_false_positive", methods=["POST"])
def mark_false_positive():
    """Mark a URL as false positive"""
    try:
        data = request.get_json()
        url = data.get('url')
        timestamp = data.get('timestamp')
        admin_note = data.get('note', '')
        
        if not url:
            return jsonify({"success": False, "error": "URL required"}), 400
        
        # Extract domain
        ext = tldextract.extract(url)
        domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
        
        # Find the original log entry to get prediction details
        original_log = None
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['url'] == url and row['timestamp'] == timestamp:
                        original_log = row
                        break
        
        # Load existing false positives
        false_positives = []
        if os.path.exists(FALSE_POSITIVE_FILE):
            with open(FALSE_POSITIVE_FILE, 'r', encoding='utf-8') as f:
                false_positives = json.load(f)
        
        # Check if already marked
        already_marked = any(fp['url'] == url and fp.get('original_timestamp') == timestamp 
                            for fp in false_positives)
        
        if already_marked:
            return jsonify({
                "success": True,
                "message": "Already marked as false positive",
                "already_marked": True
            })
        
        # Create detailed false positive entry for post-analysis
        false_positive_entry = {
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),  # ISO format
            "url": url,
            "domain": domain,
            "predicted_label": original_log['prediction'] if original_log else "unknown",
            "confidence": float(original_log['probability'].replace('%', '')) / 100 if original_log and original_log.get('probability') else 0.0,
            "risk_level": original_log['risk_level'] if original_log else "unknown",
            "action_taken": original_log['action'] if original_log else "unknown",
            "original_detection_time": timestamp,
            "admin_action": "marked_false_positive",
            "admin_note": admin_note,
            # Feature information for analysis
            "detection_reason": original_log['reason'] if original_log else "unknown",
            "detailed_features": original_log['detailed_reason'] if original_log else "unknown"
        }
        
        false_positives.append(false_positive_entry)
        
        # Save updated list
        with open(FALSE_POSITIVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(false_positives, f, indent=2, ensure_ascii=False)
        
        print(f"✅ False Positive Logged: {url}")
        print(f"   Domain: {domain}")
        print(f"   Confidence: {false_positive_entry['confidence']:.2f}")
        print(f"   Total FPs: {len(false_positives)}")
        
        return jsonify({
            "success": True,
            "message": "Marked as false positive successfully",
            "total_false_positives": len(false_positives)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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