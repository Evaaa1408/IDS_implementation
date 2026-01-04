#feature_extractor.py - CORRECTED FOR FALSE POSITIVE REDUCTION (OPTIMIZED)
import re
import math
from urllib.parse import urlparse, parse_qs
from collections import Counter
import tldextract

class URLFeatureExtractor:
    def __init__(self):
        # Suspicious keywords
        self.suspicious_keywords = [
            "login", "secure", "verify", "account", 
            "update", "confirm", "bank", "free", "bonus"
        ]
        
        # Character substitutions (typosquatting patterns, NOT brands)
        self.character_substitutions = {
            'a': ['@', '4', 'α', 'а'], 'e': ['3', 'є', 'е'],
            'i': ['1', '!', 'l', 'і'], 'o': ['0', 'ο', 'о'],
            's': ['5', '$', 'ѕ'], 'l': ['1', 'i', '!', 'ӏ'],
            't': ['7', '+', 'т'], 'g': ['9', 'q'], 'b': ['8'], 'z': ['2']
        }
        
        # Suspicious TLDs
        self.suspicious_tlds = {
            'tk', 'ml', 'ga', 'cf', 'gq', 'xyz', 'top', 'work', 'click', 'link'
        }
        
        # Homograph characters
        self.homographs = {'a': 'а', 'c': 'с', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х'}
        
        # Trusted TLDs
        self.trusted_tlds = {
            'com', 'org', 'edu', 'gov', 'net', 'io', 'dev', 'app',
            'co.uk', 'ac.uk', 'gov.uk', 'edu.my', 'gov.my'
        }
        
        # Common English words for path structure detection
        self.common_words = {
            'about', 'account', 'admin', 'api', 'app', 'article', 'auth',
            'biography', 'blog', 'category', 'code', 'comment', 'contact',
            'data', 'developer', 'doc', 'docs', 'document', 'download',
            'edit', 'email', 'entries', 'entry', 'file', 'guide', 'help',
            'home', 'info', 'learn', 'list', 'login', 'news', 'oauth',
            'page', 'post', 'profile', 'project', 'reference', 'scholar',
            'search', 'settings', 'support', 'tutorial', 'user', 'video',
            'view', 'watch', 'wiki'
        }
        
    def levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein distance"""
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
        """Calculate Shannon entropy"""
        if not s:
            return 0
        counts = Counter(s)
        probs = [float(c) / len(s) for c in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    def normalized_entropy(self, s):
        """
        Calculate length-normalized Shannon entropy.
        
        Returns: float in range [0, 1]
            0 = completely predictable
            1 = maximum randomness for given length
        """
        if not s or len(s) <= 1:
            return 0.0
        
        raw_entropy = self.shannon_entropy(s)
        max_entropy = math.log2(len(s))
        
        if max_entropy == 0:
            return 0.0
        
        return raw_entropy / max_entropy

    # Compute domain statistics once
    def compute_domain_statistics(self, domain):
        if not domain:
            return {
                'vowel_ratio': 0.0,
                'alpha_chars': [],
                'vowel_count': 0,
                'total_letters': 0,
                'unique_ratio': 0.0,
                'unusual_char_ratio': 0.0
            }
        
        vowels = 'aeiou'
        unusual_chars = 'xqzj'
        
        alpha_chars = [c for c in domain.lower() if c.isalpha()]
        total_letters = len(alpha_chars)
        
        vowel_count = sum(1 for c in alpha_chars if c in vowels)
        vowel_ratio = vowel_count / max(1, total_letters)
        
        unique_chars = len(set(alpha_chars))
        unique_ratio = unique_chars / max(1, total_letters)
        
        unusual_count = sum(1 for c in domain.lower() if c in unusual_chars)
        unusual_char_ratio = unusual_count / max(1, len(domain))
        
        return {
            'vowel_ratio': vowel_ratio,
            'alpha_chars': alpha_chars,
            'vowel_count': vowel_count,
            'total_letters': total_letters,
            'unique_ratio': unique_ratio,
            'unusual_char_ratio': unusual_char_ratio
        }

    def detect_slug_pattern(self, path):
        """
        Detect human-readable URL slugs.
        Pattern: /word-word-word, Returns: 1 if slug detected, 0 otherwise
        """
        if not path or len(path) < 5:
            return 0
        
        words = re.findall(r'[a-zA-Z]{3,}', path.lower())
        readable_words = [w for w in words if w in self.common_words]
        
        if len(readable_words) >= 2:
            return 1
        
        if re.search(r'[a-z]{3,}[-_][a-z]{3,}', path.lower()):
            return 1
        
        return 0

    # Brand-agnostic typosquatting (uses precomputed stats)
    def compute_typosquatting_score(self, domain, domain_stats):
        """
        Detect typosquatting patterns WITHOUT comparing to known brands.
        Args:
            domain: domain name string
            domain_stats: precomputed statistics from compute_domain_statistics()
        Detects:
            1. Excessive repeated characters (gooogle, faceboook)
            2. Letter-number substitutions (paypa1, g00gle)
            3. Low vowel ratio (random-looking domains)
            4. Unusual character frequency (many 'x', 'q', 'z')
            5. Mixed case in domain (PhIsHiNg.com)
        Returns: float score 0-10 (higher = more suspicious)
        """
        if not domain or len(domain) < 3:
            return 0.0
        
        score = 0.0
        
        # SIGNAL 1: Excessive repeated characters
        prev_char = ''
        max_repeat = 0
        current_repeat = 1
        
        for char in domain:
            if char.isalpha():
                if char == prev_char:
                    current_repeat += 1
                    max_repeat = max(max_repeat, current_repeat)
                else:
                    current_repeat = 1
            prev_char = char
        
        if max_repeat >= 3:
            score += min(2.0, (max_repeat - 2) * 0.5)
        
        # SIGNAL 2: Letter-number substitutions
        substitution_patterns = [
            ('0', 'o'), ('1', 'i'), ('1', 'l'), ('3', 'e'),
            ('4', 'a'), ('5', 's'), ('7', 't'), ('8', 'b')
        ]
        
        has_substitution = False
        for digit, letter in substitution_patterns:
            if digit in domain and letter in domain:
                has_substitution = True
                break
        
        if has_substitution:
            score += 1.5
        
        # SIGNAL 3: Low vowel ratio (OPTIMIZED - uses precomputed)
        vowel_ratio = domain_stats['vowel_ratio']
        
        if vowel_ratio < 0.15:
            score += 2.0
        elif vowel_ratio < 0.25:
            score += 1.0
        
        # SIGNAL 4: Unusual character frequency (OPTIMIZED - uses precomputed)
        if domain_stats['unusual_char_ratio'] > 0.15:
            score += 1.5
        
        # SIGNAL 5: Character diversity (OPTIMIZED - uses precomputed)
        if len(domain_stats['alpha_chars']) > 4:
            if domain_stats['unique_ratio'] < 0.4:
                score += 1.0
        
        # SIGNAL 6: Homograph character detection
        homograph_count = sum(1 for c in domain if c in self.homographs.values())
        if homograph_count > 0:
            score += min(3.0, homograph_count * 1.5)
        
        return min(10.0, score)

    def detect_known_typosquatting_patterns(self, domain):
        """
        Detect GENERIC typosquatting patterns (NOT brand-specific).
        Patterns:
            - Common misspelling patterns (double letters where uncommon)
            - Random capitalization (typing errors)
        Returns: 1 if suspicious pattern, 0 otherwise
        """
        if not domain or len(domain) < 4:
            return 0
        
        # Pattern 1: Triple letters (very suspicious)
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char * 3 in domain.lower():
                return 1
        
        # Pattern 2: Random capitalization (PaYpAl, FaCeBoOk)
        if domain != domain.lower() and domain != domain.capitalize():
            upper_count = sum(1 for c in domain if c.isupper())
            if upper_count > 1:
                return 1
        
        return 0

    def detect_combosquatting_pattern(self, full_domain):
        """
        Detect combosquatting patterns WITHOUT brand whitelist.
        
        Combosquatting = appending common words to domain
        Example: "secure-payment-paypal.com" (not paypal.com)
        
        Returns: score 0-3
        """
        if not full_domain:
            return 0
        
        trust_words = ['secure', 'login', 'account', 'verify', 'update', 
                      'confirm', 'support', 'help', 'payment', 'bank']
        
        domain_lower = full_domain.lower()
        score = 0
        
        # Pattern 1: Multiple hyphens with trust words
        if domain_lower.count('-') >= 2:
            for word in trust_words:
                if word in domain_lower:
                    score += 1
                    break
        
        # Pattern 2: Trust word + common service
        common_services = ['pay', 'bank', 'mail', 'shop', 'store']
        has_trust = any(word in domain_lower for word in trust_words)
        has_service = any(word in domain_lower for word in common_services)
        
        if has_trust and has_service:
            score += 1
        
        # Pattern 3: Subdomain obfuscation (many dots)
        if domain_lower.count('.') >= 3:
            if has_trust:
                score += 1
        
        return min(3, score)

    # ============================================================
    # MAIN EXTRACTION METHOD
    # ============================================================
    def extract(self, url):
        """Extract features from URL with false positive fixes"""
        try:
            parsed = urlparse(url)
        except:
            parsed = urlparse("")

        hostname = parsed.hostname or ""
        path = parsed.path or ""

        # Extract domain parts
        ext = tldextract.extract(url)
        domain_name = ext.domain.lower()
        tld = ext.suffix.lower()
        subdomain = ext.subdomain.lower()
        domain_with_tld = f"{domain_name}.{tld}" if tld else domain_name
        full_domain = hostname

        # Compute domain statistics once
        domain_stats = self.compute_domain_statistics(domain_name)

        # BASIC FEATURES (23) - WITH CAPPING
        url_length = len(url)
        hostname_length = len(hostname)
        path_length = min(len(path), 120)
        
        num_dots = url.count(".")
        num_slashes = url.count("/")
        num_hyphens = url.count("-")
        
        num_special_char_raw = sum(not c.isalnum() for c in url)
        num_special_char = min(num_special_char_raw, 25)
        
        num_at = url.count("@")
        num_percent = url.count("%")
        num_equal = url.count("=")
        
        digits = self.count_digits(url)
        letters = self.count_letters(url)
        
        digit_ratio_raw = digits / max(1, len(url))
        digit_ratio = min(digit_ratio_raw, 0.5)
        
        letter_ratio = letters / max(1, len(url))
        contains_ip = int(bool(re.search(r"\d+\.\d+\.\d+\.\d+", url)))
        uses_https = int(parsed.scheme == "https")
        subdomain_depth = hostname.count(".") - 1 if hostname else 0
        
        keyword_found = any(kw in url.lower() for kw in self.suspicious_keywords)
        suspicious_flag = int(keyword_found)
        
        tld_length = len(tld)
        hostname_ratio = hostname_length / max(1, url_length)
        path_ratio = path_length / max(1, url_length)

        # ============================================================
        # NORMALIZED ENTROPY
        # ============================================================
        url_entropy = self.normalized_entropy(url)
        domain_entropy = self.normalized_entropy(hostname)
        path_entropy = self.normalized_entropy(path)

        # ============================================================
        # DOMAIN TRUST SCORE (TLD-based only)
        # ============================================================
        domain_trust_score = 0.0
        if tld in self.trusted_tlds:
            domain_trust_score = 0.3
        elif tld in self.suspicious_tlds:
            domain_trust_score = -0.5

        # ============================================================
        # BUILD FEATURE DICTIONARY (34 FEATURES)
        # ============================================================
        features = {
            # Basic features (23)
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
            
            # Entropy features (normalized)
            "url_entropy": url_entropy,
            "domain_entropy": domain_entropy,
            "path_entropy": path_entropy,
            
            "domain_trust_score": domain_trust_score,
        }

        # ========================================================
        # ADVANCED PATTERN FEATURES (10) - BRAND-AGNOSTIC
        # ========================================================
        
        # Character substitutions
        substitution_count = 0
        for char, substitutes in self.character_substitutions.items():
            for sub in substitutes:
                if sub in domain_name:
                    substitution_count += domain_name.count(sub)
        features['CharacterSubstitutions'] = min(substitution_count, 10)
        
        # OPTIMIZED: Brand-agnostic typosquatting (uses precomputed stats)
        features['TyposquattingScore'] = self.compute_typosquatting_score(domain_name, domain_stats)
        
        # Generic typosquatting patterns
        features['KnownTyposquatting'] = self.detect_known_typosquatting_patterns(domain_name)
        
        # Homographs
        homograph_count = sum(1 for char in domain_name if char in self.homographs.values())
        features['HomographChars'] = min(homograph_count, 5)
        
        # Brand-agnostic combosquatting
        features['Combosquatting'] = self.detect_combosquatting_pattern(full_domain)
        
        # Suspicious TLD
        features['SuspiciousTLD'] = 1 if tld in self.suspicious_tlds else 0
        
        # Excessive hyphens
        features['ExcessiveHyphens'] = 1 if num_hyphens >= 3 else 0
        
        # Number-letter mixing
        mixed = re.search(r'[a-z]+\d+[a-z]+', domain_name) or re.search(r'\d+[a-z]+\d+', domain_name)
        features['NumberLetterMixing'] = 1 if mixed else 0
        
        # OPTIMIZED: Low vowel ratio (uses precomputed stats)
        features['LowVowelRatio'] = 1 if domain_stats['vowel_ratio'] < 0.25 else 0
        
        # Repeated characters
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

        # Slug detection
        features['is_slug_like'] = self.detect_slug_pattern(path)

        return features


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    extractor = ChangedURLFeatureExtractor()
    
    print("\n" + "="*70)
    print(" TESTING OPTIMIZED BRAND-AGNOSTIC DETECTION")
    print("="*70)
    
    test_urls = [
        ("https://www.britannica.com/biography/Che-Guevara", "Britannica (Legit)"),
        ("https://docs.google.com/document/d/1A9f8KJ9P2wQxU4Y/edit", "Google Docs (Legit)"),
        ("https://g00gle-verify.tk", "Phishing (g00gle)"),
        ("https://paypa1-secure.com", "Phishing (paypa1)"),
        ("https://faceboook-login.xyz", "Phishing (faceboook)"),
        ("https://xzqkrptl.tk", "Phishing (random)"),
    ]
    
    print("\n Feature Analysis:")
    print("-"*90)
    
    for url, desc in test_urls:
        features = extractor.extract(url)
        
        print(f"\n{desc}: {url[:60]}...")
        print(f"  TyposquattingScore:     {features['TyposquattingScore']:.2f}")
        print(f"  LowVowelRatio:          {features['LowVowelRatio']}")
        print(f"  KnownTyposquatting:     {features['KnownTyposquatting']}")
        print(f"  Combosquatting:         {features['Combosquatting']}")
        print(f"  is_slug_like:           {features['is_slug_like']}")