#feature_extractor.py - CORRECTED VERSION (FALSE POSITIVE FIX)
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

        # Legitimate brand domains (EXPANDED)
        self.legitimate_brands = {
            'google.com', 'facebook.com', 'instagram.com', 'twitter.com',
            'paypal.com', 'amazon.com', 'apple.com', 'microsoft.com',
            'netflix.com', 'linkedin.com', 'youtube.com', 'ebay.com',
            'walmart.com', 'target.com', 'bankofamerica.com', 'chase.com',
            'github.com', 'reddit.com', 'wikipedia.org', 'stackoverflow.com',
            'claude.ai', 'openai.com', 'chat.openai.com', 'anthropic.com',
            'whatsapp.com', 'telegram.org', 'signal.org', 'discord.com',
            'slack.com', 'zoom.us', 'teams.microsoft.com', 'notion.so',
            'figma.com', 'canva.com', 'dropbox.com', 'drive.google.com',
            'docs.google.com', 'sheets.google.com', 'medium.com',
            'substack.com', 'dev.to', 'hashnode.com', 'geeksforgeeks.org',
            'w3schools.com', 'tutorialspoint.com', 'coursera.org', 'edx.org',
            'udemy.com', 'khanacademy.org', 'bing.com', 'duckduckgo.com',
            'apu.edu.my', 'apspace.apu.edu.my', 'apiit.edu.my',
            'britannica.com', 'plato.stanford.edu', 'stanford.edu',
            'scholar.google.com', 'mozilla.org', 'developer.mozilla.org',
            'auth0.com', 'vimeo.com', 'nsf.gov', 'baseball-almanac.com',
            'americansongwriter.com', 'login.microsoftonline.com',
            'accounts.google.com'
        }
        
        # Character substitutions (typosquatting)
        self.character_substitutions = {
            'a': ['@', '4', 'α', 'а'], 'e': ['3', 'є', 'е'],
            'i': ['1', '!', 'l', 'і'], 'o': ['0', 'ο', 'о'],
            's': ['5', '$', 'ѕ'], 'l': ['1', 'i', '!', 'ӏ'],
            't': ['7', '+', 'т'], 'g': ['9', 'q'], 'b': ['8'], 'z': ['2']
        }
        
        # Typosquatting variations
        self.brand_names = {
            'google': ['g00gle', 'gooogle', 'gogle', 'googel', 'goog1e'],
            'facebook': ['faceb00k', 'facebok', 'facebbok', 'faceboook'],
            'instagram': ['inst@gram', 'insta9ram', 'instagran', 'instgram'],
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
            'site', 'website', 'space'  # Removed 'info', 'biz' (too common)
        }
        
        # Homograph characters
        self.homographs = {
            'a': 'а', 'c': 'с', 'e': 'е',
            'o': 'о', 'p': 'р', 'x': 'х',
        }
        
        # Trusted TLDs (expanded)
        self.trusted_tlds = {
            'com', 'org', 'edu', 'gov', 'net',
            'co.uk', 'ac.uk', 'gov.uk',
            'edu.au', 'gov.au', 'com.au',
            'edu.my', 'gov.my', 'com.my',
            'edu.sg', 'gov.sg', 'com.sg',
            'ac.in', 'edu.in', 'gov.in',
            'edu.cn', 'gov.cn',
            'ac.jp', 'go.jp', 'co.jp',
            'edu.hk', 'gov.hk',
            'edu.tw', 'gov.tw',
            'ac.nz', 'govt.nz', 'co.nz',
            'edu.ph', 'gov.ph',
            'io', 'dev', 'app',
        }
        
        # ============================================================
        # CRITICAL FIX 1: Common English words (for path validation)
        # ============================================================
        self.common_words = {
            'about', 'account', 'add', 'admin', 'after', 'all', 'also', 'and',
            'api', 'app', 'application', 'archive', 'article', 'auth', 'author',
            'avatar', 'back', 'before', 'best', 'biography', 'blog', 'book',
            'browse', 'business', 'calendar', 'call', 'can', 'card', 'career',
            'category', 'check', 'code', 'comment', 'common', 'company', 'contact',
            'content', 'create', 'current', 'data', 'database', 'date', 'day',
            'delete', 'design', 'developer', 'directory', 'discuss', 'doc', 'docs',
            'document', 'download', 'edit', 'email', 'entries', 'entry', 'error',
            'event', 'example', 'export', 'file', 'filter', 'find', 'first',
            'flow', 'folder', 'follow', 'for', 'form', 'forum', 'from', 'get',
            'global', 'group', 'guide', 'help', 'history', 'home', 'how', 'html',
            'http', 'https', 'image', 'import', 'index', 'info', 'information',
            'intro', 'item', 'javascript', 'join', 'key', 'language', 'last',
            'latest', 'learn', 'library', 'list', 'live', 'local', 'location',
            'login', 'logo', 'main', 'make', 'manage', 'manual', 'map', 'math',
            'media', 'member', 'menu', 'message', 'method', 'model', 'module',
            'more', 'music', 'name', 'new', 'news', 'next', 'note', 'now',
            'number', 'oauth', 'oauth2', 'object', 'old', 'online', 'open',
            'option', 'order', 'org', 'other', 'our', 'out', 'over', 'overview',
            'page', 'paper', 'parent', 'path', 'people', 'personal', 'photo',
            'picture', 'place', 'plan', 'play', 'plugin', 'point', 'policy',
            'post', 'power', 'press', 'previous', 'privacy', 'private', 'problem',
            'product', 'profile', 'program', 'project', 'promise', 'public',
            'publication', 'publish', 'query', 'question', 'quick', 'read',
            'recent', 'reference', 'register', 'release', 'remove', 'report',
            'request', 'research', 'resource', 'result', 'return', 'review',
            'right', 'room', 'roster', 'route', 'rule', 'run', 'save', 'school',
            'scholar', 'science', 'search', 'section', 'secure', 'security',
            'see', 'select', 'send', 'server', 'service', 'session', 'set',
            'setting', 'share', 'show', 'sign', 'signin', 'signup', 'site',
            'source', 'space', 'special', 'start', 'state', 'static', 'status',
            'step', 'store', 'story', 'string', 'structure', 'student', 'study',
            'style', 'submit', 'support', 'system', 'table', 'tag', 'task',
            'team', 'teamstats', 'tech', 'technology', 'template', 'term', 'test',
            'text', 'the', 'theme', 'theory', 'thing', 'this', 'time', 'title',
            'tool', 'topic', 'total', 'track', 'trade', 'transaction', 'tree',
            'tutorial', 'type', 'update', 'upload', 'url', 'use', 'user',
            'utility', 'value', 'version', 'video', 'view', 'watch', 'way',
            'web', 'week', 'welcome', 'what', 'when', 'where', 'which', 'who',
            'wiki', 'window', 'with', 'work', 'world', 'write', 'year', 'you',
            'your', 'zone', 'ethics', 'algebra', 'systems', 'equations',
            'phishing', 'detection', 'azure', 'active', 'develop', 'authorize',
            'common', 'netsec', 'comments', 'models', 'award', 'disney',
            'music', 'folds', 'lyric', 'street', 'records', 'songwriter',
            'almanac', 'baseball', 'philosophy', 'encyclopedia', 'britannica'
        }

    def levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein distance (unchanged)"""
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

    # ============================================================
    # CRITICAL FIX 2: Proper Path Structure Detection
    # ============================================================
    def analyze_path_structure(self, path):
        """
        Analyze if path contains human-readable structure.
        
        Returns dict with:
            - has_readable_words: bool
            - word_ratio: float (0-1)
            - has_slug_pattern: bool
            - segment_count: int
        """
        if not path or len(path) < 3:
            return {
                'has_readable_words': False,
                'word_ratio': 0.0,
                'has_slug_pattern': False,
                'segment_count': 0
            }
        
        # Remove leading/trailing slashes and split
        clean_path = path.strip('/')
        segments = [s for s in clean_path.split('/') if s]
        
        # Count readable words in path
        words_in_path = re.findall(r'[a-zA-Z]{3,}', path.lower())
        readable_words = [w for w in words_in_path if w in self.common_words]
        
        word_ratio = len(readable_words) / max(1, len(words_in_path))
        
        # Detect slug pattern (word-word-word)
        has_slug = bool(re.search(r'[a-z]{2,}-[a-z]{2,}', path.lower()))
        
        return {
            'has_readable_words': len(readable_words) >= 2,
            'word_ratio': word_ratio,
            'has_slug_pattern': has_slug,
            'segment_count': len(segments)
        }

    # ============================================================
    # CRITICAL FIX 3: Query Parameter Analysis
    # ============================================================
    def analyze_query_params(self, url):
        """
        Analyze query parameters for legitimacy indicators.
        
        Legitimate patterns:
            - ?v=xxx (YouTube)
            - ?q=xxx (Google Scholar)
            - ?hl=en (language)
            - ?id=xxx (generic ID)
        """
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if not params:
                return {
                    'has_query': False,
                    'common_param_count': 0
                }
            
            # Common legitimate parameters
            common_params = {'v', 'q', 'id', 'hl', 'lang', 'page', 'p', 
                           'ref', 's', 'src', 'utm_source', 'type', 't', 'y'}
            
            common_found = sum(1 for p in params.keys() if p in common_params)
            
            return {
                'has_query': True,
                'common_param_count': common_found
            }
        except:
            return {
                'has_query': False,
                'common_param_count': 0
            }

    def is_legitimate_domain(self, domain_with_tld):
        """Check if domain is whitelisted (strict exact match)"""
        clean_domain = domain_with_tld
        prefixes = ['www.', 'm.', 'mobile.']
        for prefix in prefixes:
            if clean_domain.startswith(prefix):
                clean_domain = clean_domain[len(prefix):]
        return clean_domain in self.legitimate_brands

    # ============================================================
    # CRITICAL FIX 4: Legitimacy Score (Replaces domain_trust_score)
    # ============================================================
    def calculate_legitimacy_score(self, url, domain_with_tld, tld, path, 
                                   path_analysis, query_analysis):
        """
        Calculate overall legitimacy score based on multiple signals.
        
        POSITIVE signals (legitimate):
            +0.5: Whitelisted domain
            +0.3: Trusted TLD (.edu, .gov, .org)
            +0.2: Readable words in path (>50%)
            +0.1: Common query parameters
            +0.1: Slug pattern in path
            +0.1: Multiple path segments (structured)
        
        NEGATIVE signals (suspicious):
            -0.6: Suspicious TLD (.tk, .ml, etc.)
            -0.2: No readable structure in long path
        
        Returns: float in range [-1.0, 1.0]
        """
        score = 0.0
        
        # Strong positive: Whitelisted
        if self.is_legitimate_domain(domain_with_tld):
            score += 0.5
        
        # Positive: Trusted TLD
        if tld in self.trusted_tlds:
            score += 0.3
        
        # Strong negative: Suspicious TLD
        if tld in self.suspicious_tlds:
            score -= 0.6
        
        # Path structure analysis
        if path_analysis['has_readable_words']:
            score += 0.2
        
        if path_analysis['word_ratio'] > 0.5:
            score += 0.1
        
        if path_analysis['has_slug_pattern']:
            score += 0.1
        
        if path_analysis['segment_count'] >= 3:
            score += 0.1
        
        # Long path without readable structure = suspicious
        if len(path) > 50 and not path_analysis['has_readable_words']:
            score -= 0.2
        
        # Query parameters
        if query_analysis['common_param_count'] > 0:
            score += 0.1
        
        return max(-1.0, min(1.0, score))

    # ============================================================
    # MAIN EXTRACTION METHOD - COMPLETELY REWRITTEN
    # ============================================================
    def extract(self, url):
        """Extract features from URL (CORRECTED VERSION)"""
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

        # ============================================================
        # BASIC FEATURES (23) - Keep for compatibility
        # ============================================================
        url_length = len(url)
        hostname_length = len(hostname)
        path_length = len(path)
        num_dots = url.count(".")
        num_slashes = url.count("/")
        num_hyphens = url.count("-")
        num_special_char = sum(not c.isalnum() for c in url)
        num_at = url.count("@")
        num_percent = url.count("%")
        num_equal = url.count("=")
        digits = self.count_digits(url)
        letters = self.count_letters(url)
        digit_ratio = digits / max(1, len(url))
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
        # CRITICAL FIX 5: CORRECTED ENTROPY (Keep old names!)
        # ============================================================
        # Calculate raw entropy (for compatibility)
        url_entropy = self.shannon_entropy(url)
        domain_entropy = self.shannon_entropy(hostname)
        path_entropy = self.shannon_entropy(path)
        
        # ============================================================
        # NEW: Path structure analysis
        # ============================================================
        path_analysis = self.analyze_path_structure(path)
        query_analysis = self.analyze_query_params(url)
        
        # ============================================================
        # CRITICAL FIX 6: Legitimacy score (replaces domain_trust_score)
        # ============================================================
        legitimacy_score = self.calculate_legitimacy_score(
            url, domain_with_tld, tld, path, path_analysis, query_analysis
        )

        # ============================================================
        # Build feature dictionary (SAME 33 FEATURES as original)
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
            
            # Entropy features (KEEP OLD NAMES - raw entropy)
            "url_entropy": url_entropy,
            "domain_entropy": domain_entropy,
            "path_entropy": path_entropy,
            
            # MODIFIED: Legitimacy score (replaces domain_trust_score)
            "domain_trust_score": legitimacy_score,
        }

        # ========================================================
        # Advanced pattern features (10) - ALWAYS CALCULATE
        # NO CONDITIONAL SUPPRESSION!
        # ========================================================
        
        # Character substitutions
        substitution_count = 0
        for char, substitutes in self.character_substitutions.items():
            for sub in substitutes:
                if sub in domain_name:
                    substitution_count += domain_name.count(sub)
        features['CharacterSubstitutions'] = min(substitution_count, 10)
        
        # Typosquatting - distance from known brands
        min_distance = float('inf')
        for brand in self.legitimate_brands:
            brand_domain = brand.split('.')[0]
            distance = self.levenshtein_distance(domain_name, brand_domain)
            if distance < min_distance:
                min_distance = distance
        features['TyposquattingScore'] = (3 - min_distance) if (0 < min_distance <= 2) else 0
        
        # Known typosquatting variations
        typosquatting_detected = 0
        for brand, variations in self.brand_names.items():
            if domain_name in variations or any(var in domain_name for var in variations):
                typosquatting_detected = 1
                break
        features['KnownTyposquatting'] = typosquatting_detected
        
        # Homograph characters
        homograph_count = sum(1 for char in domain_name if char in self.homographs.values())
        features['HomographChars'] = min(homograph_count, 5)
        
        # Combosquatting - brand name in non-brand domain
        combosquatting_score = 0
        brand_keywords = ['google', 'facebook', 'paypal', 'amazon', 'apple', 
                          'microsoft', 'youtube', 'github', 'netflix', 'twitter']
        for brand in brand_keywords:
            if brand in full_domain.lower():
                # Check if this is NOT the actual brand domain
                ext_check = tldextract.extract(url)
                actual_domain = f"{ext_check.domain}.{ext_check.suffix}".lower()
                
                # If domain contains brand name but isn't the brand's actual domain
                if brand in actual_domain and actual_domain not in [f"{brand}.com", f"{brand}.org", f"{brand}.net", f"{brand}.io"]:
                    combosquatting_score += 1
        features['Combosquatting'] = min(combosquatting_score, 3)
        
        # Suspicious TLD
        features['SuspiciousTLD'] = 1 if tld in self.suspicious_tlds else 0
        
        # Excessive hyphens
        features['ExcessiveHyphens'] = 1 if num_hyphens >= 3 else 0
        
        # Number-letter mixing in domain
        mixed_pattern = 0
        if re.search(r'[a-z]+\d+[a-z]+', domain_name) or re.search(r'\d+[a-z]+\d+', domain_name):
            mixed_pattern = 1
        features['NumberLetterMixing'] = mixed_pattern
        
        # Low vowel ratio
        vowels = 'aeiou'
        domain_vowels = sum(1 for c in domain_name if c in vowels)
        total_letters = sum(1 for c in domain_name if c.isalpha())
        vowel_ratio = domain_vowels / max(1, total_letters)
        features['LowVowelRatio'] = 1 if vowel_ratio < 0.25 else 0
        
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
        
        # ========================================================
        # NEW: POSITIVE LEGITIMACY SIGNALS (5 features)
        # ========================================================
        
        # Path structure quality
        features['path_has_readable_words'] = int(path_analysis['has_readable_words'])
        features['path_word_ratio'] = path_analysis['word_ratio']
        features['has_slug_pattern'] = int(path_analysis['has_slug_pattern'])
        features['path_segment_count'] = min(path_analysis['segment_count'], 10)
        features['common_query_params'] = min(query_analysis['common_param_count'], 5)
        
        return features

# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    extractor = URLFeatureExtractor()
    
    print("\n" + "="*70)
    print(" TESTING CORRECTED FEATURE EXTRACTOR")
    print("="*70)
    
    test_urls = [
        ("https://www.britannica.com/biography/Che-Guevara", "Britannica"),
        ("https://plato.stanford.edu/entries/ethics-ai/", "Stanford Philosophy"),
        ("https://scholar.google.com/scholar?hl=en&q=phishing+detection", "Google Scholar"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "YouTube"),
        ("https://github.com/openai/gpt-4/blob/main/system_card.md", "GitHub"),
        ("https://g00gle.com/verify-account", "PHISHING"),
    ]
    
    print("\n🔍 Feature Comparison:")
    print("-"*70)
    
    for url, desc in test_urls:
        features = extractor.extract(url)
        print(f"\n{desc}: {url[:60]}...")
        print(f"  Legitimacy Score: {features['domain_trust_score']:.2f}")
        print(f"  Path Entropy:     {features['path_entropy']:.2f}")
        print(f"  Combosquatting:   {features['Combosquatting']}")
        print(f"  TyposquattingScore: {features['TyposquattingScore']}")