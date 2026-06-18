from app import create_pdf_report

sample_scan = {
    'id': 'sample-report',
    'target': 'http://example.com',
    'scan_time': '2026-06-18 12:00:00',
    'max_pages': 5,
    'visited_pages': 3,
    'vulnerabilities': [
        {
            'type': 'xss',
            'severity': 'High',
            'description': 'Reflected XSS detected',
            'url': 'http://example.com/search?q=test',
            'evidence': 'Payload reflected in response',
            'details': {'payload': '<script>alert(1)</script>'}
        },
        {
            'type': 'sqli',
            'severity': 'High',
            'description': 'SQL injection error pattern',
            'url': 'http://example.com/login',
            'evidence': 'SQL syntax error displayed',
            'details': {'payload': "' OR '1'='1"}
        },
        {
            'type': 'csrf',
            'severity': 'Medium',
            'description': 'Missing CSRF token on form',
            'url': 'http://example.com/settings',
            'evidence': 'POST form without anti-CSRF field',
            'details': {'method': 'post'}
        }
    ]
}

pdf = create_pdf_report(sample_scan)
with open('sample-scan-report.pdf', 'wb') as f:
    f.write(pdf.read())
print('sample-scan-report.pdf created')
