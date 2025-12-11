#feature_extract_2023.py
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from difflib import SequenceMatcher
import tldextract

class ContentFeatureExtractor:
    def __init__(self):
        self.timeout = 10
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_similarity(self, a, b):
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, str(a), str(b)).ratio() * 100

    def extract_from_html(self, html, url):
        """
        Extract features from provided HTML content (No Fetching).
        Useful for API/Extension where HTML is sent by the client.
        """
        features = {}
        
        # Default values
        content_features = [
            'LineOfCode', 'LargestLineLength', 'HasTitle', 'DomainTitleMatchScore', 
            'URLTitleMatchScore', 'HasFavicon', 'Robots', 'IsResponsive', 
            'NoOfURLRedirect', 'NoOfSelfRedirect', 'HasDescription', 'NoOfPopup', 
            'NoOfiFrame', 'HasExternalFormSubmit', 'HasSocialNet', 'HasSubmitButton', 
            'HasHiddenFields', 'HasPasswordField', 'Bank', 'Pay', 'Crypto', 
            'HasCopyrightInfo', 'NoOfImage', 'NoOfCSS', 'NoOfJS', 'NoOfSelfRef', 
            'NoOfEmptyRef', 'NoOfExternalRef'
        ]
        
        for f in content_features:
            features[f] = 0

        try:
            # Parse URL for comparison
            ext = tldextract.extract(url)
            domain = f"{ext.domain}.{ext.suffix}"
            
            content = html
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Line Counts
            lines = content.splitlines()
            features['LineOfCode'] = len(lines)
            features['LargestLineLength'] = max(len(line) for line in lines) if lines else 0
            
            # 2. Title & Similarity
            title_tag = soup.find('title')
            features['HasTitle'] = 1 if title_tag else 0
            title_text = title_tag.text.strip() if title_tag else ""
            features['DomainTitleMatchScore'] = self.get_similarity(domain, title_text)
            features['URLTitleMatchScore'] = self.get_similarity(url, title_text)
            
            # 3. Favicon
            icon_link = soup.find("link", rel=lambda x: x and 'icon' in x.lower())
            features['HasFavicon'] = 1 if icon_link else 0
            
            # 4. Robots
            features['Robots'] = 1 if 'robots' in content.lower() else 0
            
            # 5. Responsive
            features['IsResponsive'] = 1 if soup.find('meta', attrs={'name': 'viewport'}) else 0
            
            # 6. Redirects (Cannot track history from raw HTML, set to 0 or pass as arg)
            features['NoOfURLRedirect'] = 0 
            features['NoOfSelfRedirect'] = 0 
            
            # 7. Description
            desc = soup.find('meta', attrs={'name': 'description'})
            features['HasDescription'] = 1 if desc else 0
            
            # 8. Popups & iFrames
            features['NoOfPopup'] = content.lower().count('window.open')
            features['NoOfiFrame'] = len(soup.find_all('iframe'))
            
            # 9. Forms & Fields
            forms = soup.find_all('form')
            features['HasSubmitButton'] = 1 if soup.find('input', type='submit') or soup.find('button', type='submit') else 0
            features['HasHiddenFields'] = 1 if soup.find('input', type='hidden') else 0
            features['HasPasswordField'] = 1 if soup.find('input', type='password') else 0
            
            ext_form = 0
            for form in forms:
                action = form.get('action', '')
                if action.startswith('http') and domain not in action:
                    ext_form = 1
                    break
            features['HasExternalFormSubmit'] = ext_form
            
            # 10. Social Nets
            socials = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com']
            features['HasSocialNet'] = 1 if any(s in content.lower() for s in socials) else 0
            
            # 11. Keywords
            text_content = soup.get_text().lower()
            features['Bank'] = 1 if 'bank' in text_content else 0
            features['Pay'] = 1 if 'pay' in text_content else 0
            features['Crypto'] = 1 if 'crypto' in text_content or 'bitcoin' in text_content else 0
            features['HasCopyrightInfo'] = 1 if 'copyright' in text_content or '©' in text_content else 0
            
            # 12. Resource Counts
            features['NoOfImage'] = len(soup.find_all('img'))
            features['NoOfCSS'] = len(soup.find_all('link', rel='stylesheet')) + len(soup.find_all('style'))
            features['NoOfJS'] = len(soup.find_all('script'))
            
            # 13. References
            anchors = soup.find_all('a')
            self_ref = 0
            empty_ref = 0
            ext_ref = 0
            for a in anchors:
                href = a.get('href', '')
                if not href or href == '#' or href.startswith('javascript'):
                    empty_ref += 1
                elif domain in href or href.startswith('/'):
                    self_ref += 1
                else:
                    ext_ref += 1
            
            features['NoOfSelfRef'] = self_ref
            features['NoOfEmptyRef'] = empty_ref
            features['NoOfExternalRef'] = ext_ref
            
        except Exception as e:
            # print(f"Error parsing HTML: {e}")
            pass

        return features

    def extract(self, url):
        """
        Fetches the URL and then extracts features.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            # We can pass response.history to extract_from_html if we modify it, 
            # but for now we keep it simple.
            # Ideally, extract_from_html should handle the parsing logic.
            
            features = self.extract_from_html(response.text, url)
            
            # Add redirect count which is only available from response
            features['NoOfURLRedirect'] = len(response.history)
            
            return features
            
        except Exception as e:
            # Return empty/zero features on failure
            return self.extract_from_html("", url)

if __name__ == "__main__":
    extractor = ContentFeatureExtractor()
    print(extractor.extract("https://google.com"))
