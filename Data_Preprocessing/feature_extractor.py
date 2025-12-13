#feature_extractor.py (FIXED VERSION)
import re
import math
from urllib.parse import urlparse
from collections import Counter
import tldextract

class URLFeatureExtractor:
    def __init__(self):
        # Suspicious keywords based on phishing research
        self.suspicious_keywords = [
            "login", "secure", "verify", "account", 
            "update", "confirm", "bank", "free", "bonus"
        ]

        # Legitimate brand domains 
        self.legitimate_brands = {
            'google.com', 'facebook.com', 'instagram.com', 'twitter.com',
            'paypal.com', 'amazon.com', 'apple.com', 'microsoft.com',
            'netflix.com', 'linkedin.com', 'youtube.com', 'ebay.com',
            'walmart.com', 'target.com', 'bankofamerica.com', 'chase.com',
            'github.com', 'reddit.com', 'wikipedia.org', 'stackoverflow.com',
            # AI Tools & Services
            'claude.ai', 'openai.com', 'chat.openai.com', 'anthropic.com',
            'google.ai', 'gemini.google.com', 'bard.google.com',
            'huggingface.co', 'midjourney.com', 'character.ai',
            # Messaging Apps
            'whatsapp.com', 'web.whatsapp.com', 'telegram.org', 'signal.org',
            'discord.com', 'slack.com', 'zoom.us', 'teams.microsoft.com',
            # Popular Tech Sites
            'notion.so', 'figma.com', 'canva.com', 'dropbox.com',
            'drive.google.com', 'docs.google.com', 'sheets.google.com',
            # Tech Blogs & News
            'comparitech.com', 'techcrunch.com', 'theverge.com', 'wired.com',
            'cnet.com', 'zdnet.com', 'arstechnica.com', 'engadget.com',
            'mashable.com', 'gizmodo.com', 'lifehacker.com', 'howtogeek.com',
            # Educational & Reference
            'medium.com', 'substack.com', 'dev.to', 'hashnode.com',
            'geeksforgeeks.org', 'w3schools.com', 'tutorialspoint.com',
            'coursera.org', 'edx.org', 'udemy.com', 'khanacademy.org',
            # Search Engines
            'bing.com', 'duckduckgo.com', 'yahoo.com', 'baidu.com',
            'yandex.com', 'search.yahoo.com', 'search.brave.com',
            # Universities (Malaysia & Asia)
            'apu.edu.my', 'apiit.edu.my', 'lms2.apiit.edu.my',
            'um.edu.my', 'usm.my', 'upm.edu.my',
            'utm.my', 'ukm.my', 'nus.edu.sg', 'ntu.edu.sg'
        }
        
        # Character substitutions used in typosquatting
        self.character_substitutions = {
            'a': ['@', '4', 'α', 'а'],
            'e': ['3', 'є', 'е'],
            'i': ['1', '!', 'l', 'і'],
            'o': ['0', 'ο', 'о'],
            's': ['5', '$', 'ѕ'],
            'l': ['1', 'i', '!', 'ӏ'],
            't': ['7', '+', 'т'],
            'g': ['9', 'q'],
            'b': ['8'],
            'z': ['2']
        }
        
        # Common brand names to check for typosquatting
        self.brand_names = {
            'google': ['g00gle', 'gooogle', 'gogle', 'googel', 'goog1e'],
            'facebook': ['faceb00k', 'facebok', 'facebbok', 'faceboook', 'faceook'],
            'instagram': ['inst@gram', 'insta9ram', 'instagran', 'instgram', 'inst4gram'],
            'paypal': ['p@ypal', 'payp@l', 'paypai', 'paypa1', 'paypall'],
            'amazon': ['amaz0n', '@mazon', 'amazom', 'arnazon', 'amazan'],
            'microsoft': ['micros0ft', 'microsft', 'micro$oft', 'micorsoft'],
            'apple': ['@pple', 'appl3', 'appie', 'app1e'],
            'netflix': ['netf1ix', 'netfllx', 'netfli><', 'netf!ix'],
            'twitter': ['tw1tter', 'twtter', 'twiter', 'twltter'],
            'linkedin': ['link3din', 'linkedln', 'linkdin'],
            'youtube': ['yout00be', 'youtub3', 'y0utube', 'youtbe'],
            'github': ['githubb', 'githb', 'gith0b', 'git-hub']
        }
        
        # Suspicious TLDs
        self.suspicious_tlds = {
            'tk', 'ml', 'ga', 'cf', 'gq',
            'xyz', 'top', 'work', 'click', 'link', 'online',
            'site', 'website', 'space', 'info', 'biz'
        }
        
        # Homograph characters
        self.homographs = {
            'a': 'а',
            'c': 'с',
            'e': 'е',
            'o': 'о',
            'p': 'р',
            'x': 'х',
        }

    def levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def count_digits(self, text):
        return sum(c.isdigit() for c in text)

    def count_letters(self, text):
        return sum(c.isalpha() for c in text)

    def shannon_entropy(self, s):
        if not s:
            return 0
        counts = Counter(s)
        probs = [float(c) / len(s) for c in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    def is_legitimate_domain(self, domain_with_tld):
        """
        Check if a domain is in the legitimate brands list
        Handles cases like:
        - www.youtube.com → youtube.com
        - youtube.com → youtube.com
        - m.youtube.com → youtube.com
        """
        # Remove www, m, mobile prefixes
        clean_domain = domain_with_tld
        prefixes = ['www.', 'm.', 'mobile.']
        for prefix in prefixes:
            if clean_domain.startswith(prefix):
                clean_domain = clean_domain[len(prefix):]
        
        return clean_domain in self.legitimate_brands

    def extract(self, url):
        try:
            parsed = urlparse(url)
        except:
            parsed = urlparse("")

        hostname = parsed.hostname or ""
        path = parsed.path or ""

        # Extract domain parts using tldextract
        ext = tldextract.extract(url)
        domain_name = ext.domain.lower()
        tld = ext.suffix.lower()
        subdomain = ext.subdomain.lower()
        
        # Full domain with TLD (for legitimate checking)
        domain_with_tld = f"{domain_name}.{tld}" if tld else domain_name
        full_domain = hostname

        # ----------------------------
        # Basic features (23)
        # ----------------------------
        url_length = len(url)
        hostname_length = len(hostname)
        path_length = len(path)

        # Character counts
        num_dots = url.count(".")
        num_slashes = url.count("/")
        num_hyphens = url.count("-")
        num_special_char = sum(not c.isalnum() for c in url)
        num_at = url.count("@")
        num_percent = url.count("%")
        num_equal = url.count("=")

        # Digit/Letter ratios
        digits = self.count_digits(url)
        letters = self.count_letters(url)
        digit_ratio = digits / max(1, len(url))
        letter_ratio = letters / max(1, len(url))

        # Detect IP address in URL
        contains_ip = int(bool(re.search(r"\d+\.\d+\.\d+\.\d+", url)))

        # HTTPS flag
        uses_https = int(parsed.scheme == "https")

        # Subdomain depth
        subdomain_depth = hostname.count(".") - 1 if hostname else 0

        # Suspicious keywords
        keyword_found = any(kw in url.lower() for kw in self.suspicious_keywords)
        suspicious_flag = int(keyword_found)

        # TLD length
        tld_length = len(tld)

        # Entropy
        url_entropy = self.shannon_entropy(url)
        domain_entropy = self.shannon_entropy(hostname)
        path_entropy = self.shannon_entropy(path)

        # Length ratios
        hostname_ratio = hostname_length / max(1, url_length)
        path_ratio = path_length / max(1, url_length)

        # ========================================================
        # NEW: DOMAIN TRUST SCORE
        # ========================================================
        # Calculate trust score based on TLD and domain characteristics
        domain_trust_score = 0.0
        
        # Trusted TLDs get positive score (expanded for international)
        trusted_tlds = {
            'com', 'org', 'edu', 'gov', 'net',
            'co.uk', 'ac.uk', 'gov.uk',
            'edu.au', 'gov.au', 'com.au',
            'edu.my', 'gov.my', 'com.my',  # Malaysia
            'edu.sg', 'gov.sg', 'com.sg',  # Singapore
            'ac.in', 'edu.in', 'gov.in',   # India
            'edu.cn', 'gov.cn',            # China
            'ac.jp', 'go.jp', 'co.jp',     # Japan
            'edu.hk', 'gov.hk',            # Hong Kong
            'edu.tw', 'gov.tw',            # Taiwan
            'ac.nz', 'govt.nz', 'co.nz',   # New Zealand
            'edu.ph', 'gov.ph'             # Philippines
        }
        if tld in trusted_tlds:
            domain_trust_score += 0.3
        
        # Suspicious TLDs get negative score
        if tld in self.suspicious_tlds:
            domain_trust_score -= 0.8
        
        # Well-known domains get high trust
        if domain_with_tld in self.legitimate_brands:
            domain_trust_score += 0.7
        
        # Long-established patterns (heuristic indicators of legitimacy)
        # - Reasonable domain length (not too short, not too long)
        if 5 <= len(domain_name) <= 20:
            domain_trust_score += 0.1
        
        # - Simple structure (few hyphens, no numbers in unusual places)
        if num_hyphens == 0 and digit_ratio < 0.2:
            domain_trust_score += 0.1
        
        # Normalize to [-1, 1] range
        domain_trust_score = max(-1.0, min(1.0, domain_trust_score))

        features = {
            "url_length": url_length,
            "hostname_length": hostname_length,
            "path_length": path_length,
            "hostname_ratio": hostname_ratio,
            "path_ratio": path_ratio,
            "num_dots": num_dots,
            "num_slashes": num_slashes,
            "num_hyphens": num_hyphens,
            "num_special_char": num_special_char,
            "num_at": num_at,
            "num_percent": num_percent,
            "num_equal": num_equal,
            "digit_ratio": digit_ratio,
            "letter_ratio": letter_ratio,
            "contains_ip": contains_ip,
            "uses_https": uses_https,
            "subdomain_depth": subdomain_depth,
            "tld_length": tld_length,
            "suspicious_keyword_flag": suspicious_flag,
            "url_entropy": url_entropy,
            "domain_entropy": domain_entropy,
            "path_entropy": path_entropy,
            "domain_trust_score": domain_trust_score  # NEW FEATURE
        }

        # ========================================================
        # 10 ADVANCED URL PATTERN FEATURES (FIXED)
        # ========================================================
        
        # CRITICAL FIX: Skip advanced detection for legitimate domains
        is_legitimate = self.is_legitimate_domain(domain_with_tld)
        
        if is_legitimate:
            # Zero out all suspicious features for known legitimate domains
            features['CharacterSubstitutions'] = 0
            features['TyposquattingScore'] = 0
            features['KnownTyposquatting'] = 0
            features['HomographChars'] = 0
            features['Combosquatting'] = 0
            features['SuspiciousTLD'] = 0
            features['ExcessiveHyphens'] = 0
            features['NumberLetterMixing'] = 0
            features['LowVowelRatio'] = 0
            features['RepeatedCharacters'] = 0
        else:
            # Only check advanced features for unknown domains
            
            # FEATURE 1: Character Substitution Count
            substitution_count = 0
            for char, substitutes in self.character_substitutions.items():
                for sub in substitutes:
                    if sub in domain_name:
                        substitution_count += domain_name.count(sub)
            features['CharacterSubstitutions'] = min(substitution_count, 10)
            
            # FEATURE 2: Typosquatting Detection
            min_distance = float('inf')
            for brand in self.legitimate_brands:
                brand_domain = brand.split('.')[0]
                distance = self.levenshtein_distance(domain_name, brand_domain)
                if distance < min_distance:
                    min_distance = distance
            
            if min_distance > 0 and min_distance <= 2:
                features['TyposquattingScore'] = 3 - min_distance
            else:
                features['TyposquattingScore'] = 0
            
            # FEATURE 3: Known Typosquatting Patterns
            typosquatting_detected = 0
            for brand, variations in self.brand_names.items():
                if domain_name in variations or any(var in domain_name for var in variations):
                    typosquatting_detected = 1
                    break
            features['KnownTyposquatting'] = typosquatting_detected
            
            # FEATURE 4: Homograph Attack Detection
            homograph_count = 0
            for char in domain_name:
                if char in self.homographs.values():
                    homograph_count += 1
            features['HomographChars'] = min(homograph_count, 5)
            
            # FEATURE 5: Combosquatting Detection (FIXED)
            combosquatting_score = 0
            for brand in ['google', 'facebook', 'paypal', 'amazon', 'apple', 'microsoft', 'youtube', 'github']:
                # Check if brand appears in domain but it's NOT a legitimate subdomain
                if brand in full_domain.lower():
                    # Create full brand domain
                    brand_full = f"{brand}.com"
                    
                    # Check if this is actually the legitimate domain
                    if not self.is_legitimate_domain(domain_with_tld):
                        # Brand in domain but not legitimate = combosquatting
                        # Examples: paypal-verify.com, secure-google.com
                        combosquatting_score += 1
            
            features['Combosquatting'] = min(combosquatting_score, 3)
            
            # FEATURE 6: Suspicious TLD
            features['SuspiciousTLD'] = 1 if tld in self.suspicious_tlds else 0
            
            # FEATURE 7: Excessive Hyphens
            features['ExcessiveHyphens'] = 1 if num_hyphens >= 2 else 0
            
            # FEATURE 8: Number-Letter Mixing Pattern
            mixed_pattern = 0
            if re.search(r'[a-z]+\d+[a-z]+', domain_name) or re.search(r'\d+[a-z]+\d+', domain_name):
                mixed_pattern = 1
            features['NumberLetterMixing'] = mixed_pattern
            
            # FEATURE 9: Vowel Substitution Ratio
            vowels = 'aeiou'
            domain_consonants = sum(1 for c in domain_name if c.isalpha() and c not in vowels)
            domain_vowels = sum(1 for c in domain_name if c in vowels)
            total_letters = domain_consonants + domain_vowels
            
            if total_letters > 0:
                vowel_ratio = domain_vowels / total_letters
                if vowel_ratio < 0.25:
                    features['LowVowelRatio'] = 1
                else:
                    features['LowVowelRatio'] = 0
            else:
                features['LowVowelRatio'] = 0
            
            # FEATURE 10: Repeated Characters
            repeated_chars = 0
            prev_char = ''
            repeat_count = 0
            for char in domain_name:
                if char == prev_char and char.isalpha():
                    repeat_count += 1
                    if repeat_count >= 2:
                        repeated_chars += 1
                else:
                    repeat_count = 0
                prev_char = char
            features['RepeatedCharacters'] = min(repeated_chars, 3)

        return features


if __name__ == "__main__":
    extractor = URLFeatureExtractor()
    
    print("\n" + "="*70)
    print(" TESTING FIXED URL PATTERN DETECTION")
    print("="*70)
    
    test_urls = [
        ("https://www.google.com", "Real Google - Should be SAFE"),
        ("https://www.youtube.com", "Real YouTube - Should be SAFE"),
        ("https://github.com", "Real GitHub - Should be SAFE"),
        ("https://www.facebook.com", "Real Facebook - Should be SAFE"),
        ("https://g00gle.com", "Google with zeros - PHISHING"),
        ("https://paypal-verify.com", "PayPal combosquatting - PHISHING"),
        ("https://yout00be.com", "YouTube typo - PHISHING"),
    ]
    
    print("\n🔍 Testing URLs:")
    print("-"*70)
    
    for url, description in test_urls:
        print(f"\n📝 {description}")
        print(f"   URL: {url}")
        
        features = extractor.extract(url)
        
        # Show advanced features
        advanced_features = [
            'CharacterSubstitutions', 'TyposquattingScore', 'KnownTyposquatting',
            'HomographChars', 'Combosquatting', 'SuspiciousTLD',
            'ExcessiveHyphens', 'NumberLetterMixing', 'LowVowelRatio',
            'RepeatedCharacters'
        ]
        
        suspicious_count = sum(features[f] for f in advanced_features if features[f] > 0)
        
        if suspicious_count == 0:
            print(f"   ✅ No suspicious patterns detected")
        else:
            print(f"   🚨 Suspicious patterns found:")
            for feat in advanced_features:
                if features[feat] > 0:
                    print(f"      - {feat}: {features[feat]}")
        
        print(f"   Total suspicious score: {suspicious_count}/10")
    
    print("\n" + "="*70)