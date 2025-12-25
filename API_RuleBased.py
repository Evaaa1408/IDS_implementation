#API_RuleBased.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import csv
import json
from datetime import datetime
import tldextract
from urllib.parse import urlparse

sys.path.append(os.path.dirname(__file__))

from RuleBased.Ensemble_Rulebased import RuleBasedFusionPredictor

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome Extension

# Initialize Predictor
try:
    predictor = RuleBasedFusionPredictor()
    print("Rule-Based Predictor Initialized")
except Exception as e:
    print(f"Failed to initialize predictor: {e}")
    predictor = None

# File paths
LOG_FILE = os.path.join(os.path.dirname(__file__), 'HTML_logs', 'Malicious_log.csv')
FALSE_POSITIVE_FILE = os.path.join(os.path.dirname(__file__), 'HTML_logs', 'false_positive_log.csv')

# Initialize CSV file if it doesn't exist
if not os.path.exists(LOG_FILE):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'url', 'domain', 'prediction', 'probability', 'action', 'risk_level', 'reason', 'detailed_reason'])

# Initialize false positive CSV file if it doesn't exist
if not os.path.exists(FALSE_POSITIVE_FILE):
    os.makedirs(os.path.dirname(FALSE_POSITIVE_FILE), exist_ok=True)
    with open(FALSE_POSITIVE_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['marked_at', 'original_timestamp', 'url', 'domain', 'prediction', 'probability', 'risk_level', 'action', 'reason', 'detailed_reason', 'admin_note'])

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

# FALSE POSITIVE OVERRIDE FUNCTIONS
# Cache for false positive URLs with file modification time
_fp_cache = {
    'urls': set(),
    'mtime': None
}

def normalize_url(url):
    """ Normalize URL to handle variations (trailing slashes, params, case) """
    try:
        parsed = urlparse(url)
        # Preserve scheme and netloc, normalize path
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        # Remove trailing slash and convert to lowercase for consistency
        normalized = normalized.rstrip('/').lower()
        return normalized
    except Exception as e:
        print(f"Error normalizing URL {url}: {e}")
        return url.lower()  # Fallback to lowercase only

def load_false_positive_urls():
    """ Load false positive URLs from CSV with mtime-based cache invalidation.
        This implements a post-prediction policy override based on verified false positives. """
    global _fp_cache
    
    try:
        # Check if file exists
        if not os.path.exists(FALSE_POSITIVE_FILE):
            return set()
        
        # Get current file modification time
        current_mtime = os.path.getmtime(FALSE_POSITIVE_FILE)
        
        # Return cached data if file hasn't been modified
        if _fp_cache['mtime'] == current_mtime and _fp_cache['urls']:
            return _fp_cache['urls']
        
        # File has been modified or cache is empty - reload
        fp_urls = set()
        with open(FALSE_POSITIVE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get('url', '').strip()
                if url:
                    # Normalize URL before storing
                    normalized_url = normalize_url(url)
                    fp_urls.add(normalized_url)
        
        # Update cache
        _fp_cache['urls'] = fp_urls
        _fp_cache['mtime'] = current_mtime
        
        print(f"✅ Loaded {len(fp_urls)} verified false positive URLs (cache updated)")
        return fp_urls
        
    except Exception as e:
        print(f"⚠️ Error loading false positive URLs: {e}")
        return set()

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
        print(f"Error logging to CSV: {e}")

# MAIN ENDPOINTS
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
        print(f"API REQUEST")
        print(f"{'='*70}")
        print(f"URL: {url}")
        print(f"HTML Available: {html_content is not None}")
        print(f"HTML Captured Flag: {html_captured}")
        
        # Run prediction
        result = predictor.predict(url, html_content)
        
        # POST-PREDICTION POLICY OVERRIDE FOR VERIFIED FALSE POSITIVES
        # Normalize the current URL for comparison
        normalized_url = normalize_url(url)
        
        # Load false positive URLs (cached with mtime check)
        fp_urls = load_false_positive_urls()
        
        # Check if this URL has been verified as a false positive
        is_false_positive_override = normalized_url in fp_urls
        
        # Store original model predictions (for transparency and auditing)
        model_prediction = "phishing" if result.get('is_phishing', False) else "legitimate"
        model_risk_level = result.get('risk_level', 'UNKNOWN')
        model_probability = result.get('final_risk_pct', 0.0)
        model_color = result.get('color', 'gray')
        
        # Apply post-prediction policy override if URL is verified false positive
        if is_false_positive_override:
            # Override decision - this URL was verified as safe by admin
            result['is_phishing'] = False
            result['risk_level'] = 'SAFE (FALSE POSITIVE)'
            result['final_risk_pct'] = 0.0
            result['color'] = 'blue'  # Blue indicates user-verified false positive
            result['message'] = 'This URL was previously reported as a false positive by administrators'
            
            print(f"FALSE POSITIVE OVERRIDE APPLIED")
            print(f"URL: {url}")
            print(f"Original Model Prediction: {model_prediction}")
            print(f"Final Decision: legitimate (policy override)")
        
        # Format response for browser extension
        response = {
            # Input info
            "url": url,
            "html_available": result.get('html_available', False),
            
            # Model predictions
            "url_prob": result.get('url_prob', 0.0),
            "content_prob": result.get('content_prob', 0.0),
            "model_prediction": model_prediction,
            "model_risk_level": model_risk_level,
            "model_probability": model_probability,
            
            # Final decision (after policy override if applicable)
            "final_decision": "phishing" if result.get('is_phishing', False) else "legitimate",
            "final_risk_pct": result.get('final_risk_pct', 0.0),
            "risk_level": result.get('risk_level', 'UNKNOWN'),
            "color": result.get('color', 'gray'),
            "confidence": result.get('confidence', 'UNKNOWN'),
            "is_phishing": result.get('is_phishing', False),
            "message": result.get('message', ''),
            
            # Override tracking
            "overridden": is_false_positive_override,
            "override_reason": "Verified false positive by admin" if is_false_positive_override else None,
            
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
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Dashboard Endpoints
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
        try:
            if os.path.exists(FALSE_POSITIVE_FILE):
                with open(FALSE_POSITIVE_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        false_positives.append(row)
        except Exception as csv_error:
            print(f"Error reading false positive CSV: {csv_error}")
        
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
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert CSV row to match expected frontend format
                    false_positives.append({
                        'timestamp': row['marked_at'],
                        'original_detection_time': row['original_timestamp'],
                        'url': row['url'],
                        'domain': row['domain'],
                        'predicted_label': row['prediction'],
                        'confidence': float(row['probability'].replace('%', '')) / 100 if '%' in row['probability'] else float(row['probability']),
                        'risk_level': row['risk_level'],
                        'action_taken': row['action'],
                        'detection_reason': row['reason'],
                        'detailed_features': row['detailed_reason'],
                        'admin_note': row['admin_note']
                    })
        
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
    """Mark a URL as false positive removes from malicious log and adds to false positive CSV"""
    try:
        data = request.get_json()
        url = data.get('url')
        timestamp = data.get('timestamp')
        admin_note = data.get('note', '')
        
        if not url:
            return jsonify({"success": False, "error": "URL required"}), 400
        
        # Read all logs from malicious_log.csv
        all_logs = []
        original_log = None
        
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['url'] == url and row['timestamp'] == timestamp:
                        original_log = row  # Found the entry to remove
                    else:
                        all_logs.append(row)  # Keep all other entries
        
        if not original_log:
            return jsonify({
                "success": False,
                "error": "Original log entry not found"
            }), 404
        
        # Check if already marked as false positive
        if os.path.exists(FALSE_POSITIVE_FILE):
            with open(FALSE_POSITIVE_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['url'] == url and row['original_timestamp'] == timestamp:
                        return jsonify({
                            "success": True,
                            "message": "Already marked as false positive",
                            "already_marked": True
                        })
        
        # Write back to malicious_log.csv WITHOUT the false positive entry
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'url', 'domain', 'prediction', 
                                                   'probability', 'action', 'risk_level', 
                                                   'reason', 'detailed_reason'])
            writer.writeheader()
            writer.writerows(all_logs)
        
        # Add to false_positive_log.csv
        marked_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fp_entry = {
            'marked_at': marked_timestamp,
            'original_timestamp': timestamp,
            'url': url,
            'domain': original_log['domain'],
            'prediction': original_log['prediction'],
            'probability': original_log['probability'],
            'risk_level': original_log['risk_level'],
            'action': original_log['action'],
            'reason': original_log['reason'],
            'detailed_reason': original_log['detailed_reason'],
            'admin_note': admin_note
        }
        
        # Initialize false positive CSV if it doesn't exist
        file_exists = os.path.exists(FALSE_POSITIVE_FILE)
        if not file_exists:
            with open(FALSE_POSITIVE_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(fp_entry.keys()))
                writer.writeheader()
        
        # Append to false positive CSV
        with open(FALSE_POSITIVE_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(fp_entry.keys()))
            writer.writerow(fp_entry)
        
        print(f"False Positive Marked: {url}")
        print(f"Removed from: Malicious_log.csv")
        print(f"Added to: false_positive_log.csv")
        
        return jsonify({
            "success": True,
            "message": "Marked as false positive successfully",
            "removed_from_malicious_log": True
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# HEALTH CHECK
@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "predictor": "active" if predictor else "inactive"
    })

if __name__ == "__main__":
    print("="*70)
    print("STARTING RULE-BASED PHISHING DETECTION API")
    print("="*70)
    print("Configuration:")
    print("• Method: Rule-Based Fusion")
    print("• Port: 5000")
    print("• CORS: Enabled")
    print("• DataCollector: Disabled (removed)")
    print("Endpoints:")
    print("POST /predict - Main prediction")
    print("GET /health - Health check")
    print("GET /api/stats - System stats")
    print("\n" + "="*70 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=True)        