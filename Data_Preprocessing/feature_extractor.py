import re
import math
from urllib.parse import urlparse
from collections import Counter

class URLFeatureExtractor:
    def __init__(self):
        # Suspicious keywords based on phishing research
        self.suspicious_keywords = [
            "login", "secure", "verify", "account", 
            "update", "confirm", "bank", "free", "bonus"
        ]

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

    def extract(self, url):
        try:
            parsed = urlparse(url)
        except:
            parsed = urlparse("")

        hostname = parsed.hostname or ""
        path = parsed.path or ""

        # ----------------------------
        # Basic features
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
        tld = hostname.split(".")[-1] if "." in hostname else ""
        tld_length = len(tld)

        # Entropy
        url_entropy = self.shannon_entropy(url)
        domain_entropy = self.shannon_entropy(hostname)
        path_entropy = self.shannon_entropy(path)

        # Length ratios
        hostname_ratio = hostname_length / max(1, url_length)
        path_ratio = path_length / max(1, url_length)

        return {
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
            "path_entropy": path_entropy
        }
