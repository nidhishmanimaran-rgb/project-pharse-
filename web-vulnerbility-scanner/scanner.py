import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg/onload=alert('XSS')>",
]
SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "\" OR \"1\"=\"1\"--",
]
CSRF_PATTERNS = [
    r"<input[^>]+name=[\'\"]csrf_token[\'\"]",
    r"<input[^>]+name=[\'\"]_csrf[\'\"]",
    r"<input[^>]+name=[\'\"]csrfmiddlewaretoken[\'\"]",
]

VULN_TEMPLATES = {
    "xss": {
        "severity": "High",
        "description": "Reflected cross-site scripting detected when user-supplied input is reflected in the response."
    },
    "sqli": {
        "severity": "High",
        "description": "Potential SQL injection detected from query-like input and database error patterns."
    },
    "csrf": {
        "severity": "Medium",
        "description": "Possible missing anti-CSRF token on state-changing forms."
    },
}

class Scanner:
    def __init__(self, target_url, max_pages=20):
        self.target_url = target_url.rstrip('/')
        self.max_pages = max_pages
        self.visited = set()
        self.queue = [self.target_url]
        self.vulnerabilities = []

    def fetch(self, url):
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=12, verify=False)
            return response
        except requests.RequestException:
            return None

    def get_links(self, response, base_url):
        urls = set()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag, attr in [("a", "href"), ("form", "action")]:
            for element in soup.find_all(tag):
                value = element.get(attr)
                if not value:
                    continue
                url = urljoin(base_url, value)
                if self.is_same_domain(url):
                    urls.add(url.split('#')[0])
        return urls

    def is_same_domain(self, url):
        origin = urlparse(self.target_url).netloc
        return urlparse(url).netloc == origin

    def discover_inputs(self, response):
        form_inputs = []
        soup = BeautifulSoup(response.text, 'html.parser')
        for form in soup.find_all('form'):
            action = form.get('action') or response.url
            method = form.get('method', 'get').lower()
            inputs = {}
            for field in form.find_all(['input', 'textarea', 'select']):
                name = field.get('name')
                if not name:
                    continue
                value = field.get('value', '')
                inputs[name] = value
            form_inputs.append({
                'action': urljoin(response.url, action),
                'method': method,
                'inputs': inputs,
                'html': str(form),
            })
        return form_inputs

    def scan(self):
        while self.queue and len(self.visited) < self.max_pages:
            url = self.queue.pop(0)
            if url in self.visited:
                continue
            response = self.fetch(url)
            if not response:
                continue
            self.visited.add(url)
            self.queue.extend([u for u in self.get_links(response, url) if u not in self.visited])
            forms = self.discover_inputs(response)
            for form in forms:
                self.test_form(form)
            self.test_url_for_xss(response, url)
            self.test_url_for_sqli(response, url)
            self.test_csrf_forms(forms)
        return self.vulnerabilities

    def record_vuln(self, vuln_type, evidence, url, details=None):
        details = details or {}
        template = VULN_TEMPLATES.get(vuln_type, {})
        self.vulnerabilities.append({
            'type': vuln_type,
            'severity': template.get('severity', 'Low'),
            'description': template.get('description', ''),
            'url': url,
            'evidence': evidence,
            'details': details,
        })

    def test_url_for_xss(self, response, url):
        if any(payload in response.text for payload in XSS_PAYLOADS):
            self.record_vuln('xss', 'Payload reflected in response body.', url)

    def test_url_for_sqli(self, response, url):
        error_patterns = [
            r"you have an error in your sql syntax",
            r"warning: mysql",
            r"unclosed quotation mark after the character string",
            r"quoted string not properly terminated",
        ]
        for pattern in error_patterns:
            if re.search(pattern, response.text, re.IGNORECASE):
                self.record_vuln('sqli', f"Database error pattern detected: {pattern}", url)
                return

    def test_csrf_forms(self, forms):
        for form in forms:
            if form['method'] == 'post':
                html = form['html']
                if not any(re.search(pattern, html, re.IGNORECASE) for pattern in CSRF_PATTERNS):
                    self.record_vuln('csrf', 'POST form missing CSRF token field.', form['action'], {'method': 'post'})

    def test_form(self, form):
        action = form['action']
        method = form['method']
        default_data = {name: value or 'test' for name, value in form['inputs'].items()}
        for payload in XSS_PAYLOADS:
            data = default_data.copy()
            for name in data:
                data[name] = payload
            response = self.request_form(action, method, data)
            if response and payload in response.text:
                self.record_vuln('xss', f"Reflected XSS payload in form response: {payload}", action, {'form': form})
                break
        for payload in SQLI_PAYLOADS:
            data = default_data.copy()
            for name in data:
                data[name] = payload
            response = self.request_form(action, method, data)
            if response and re.search(r"(sql syntax|mysql|sql error|syntax error|unclosed quotation mark)", response.text, re.IGNORECASE):
                self.record_vuln('sqli', f"SQL error returned after injection: {payload}", action, {'form': form})
                break

    def request_form(self, action, method, data):
        try:
            if method == 'post':
                return requests.post(action, data=data, headers=DEFAULT_HEADERS, timeout=12, verify=False)
            return requests.get(action, params=data, headers=DEFAULT_HEADERS, timeout=12, verify=False)
        except requests.RequestException:
            return None
