import io
import os
import uuid
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from scanner import Scanner
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

scan_history = []

@app.route('/')
def index():
    return render_template('index.html', scans=scan_history)

@app.route('/scan', methods=['POST'])
def scan():
    target_url = request.form.get('target_url', '').strip()
    max_pages = int(request.form.get('max_pages', 10))
    if not target_url:
        flash('Please enter a target URL.', 'danger')
        return redirect(url_for('index'))
    parsed = urlparse(target_url)
    if not parsed.scheme:
        target_url = 'http://' + target_url
    scanner = Scanner(target_url, max_pages=max_pages)
    vulnerabilities = scanner.scan()
    scan_result = {
        'id': str(uuid.uuid4()),
        'target': target_url,
        'scan_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'max_pages': max_pages,
        'visited_pages': len(scanner.visited),
        'vulnerabilities': vulnerabilities,
    }
    scan_history.insert(0, scan_result)
    return render_template('results.html', scan=scan_result)

@app.route('/download-report/<scan_id>')
def download_report(scan_id):
    scan = next((item for item in scan_history if item['id'] == scan_id), None)
    if not scan:
        flash('Report not found.', 'danger')
        return redirect(url_for('index'))
    pdf_file = create_pdf_report(scan)
    return send_file(pdf_file,
                     download_name=f"scan-report-{scan['target'].replace('://','_').replace('/','_')}.pdf",
                     as_attachment=True,
                     mimetype='application/pdf')

@app.route('/demo-scan')
def demo_scan():
    demo_result = {
        'id': 'demo-scan-' + str(uuid.uuid4()),
        'target': 'http://demo-vulnerable.local',
        'scan_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'max_pages': 5,
        'visited_pages': 4,
        'vulnerabilities': [
            {
                'type': 'xss',
                'severity': 'High',
                'description': 'Reflected XSS detected when user-supplied input is reflected in the response.',
                'url': 'http://demo-vulnerable.local/search.php?q=test',
                'evidence': 'Payload <script>alert(1)</script> reflected in search results',
                'details': {'payload': '<script>alert(1)</script>', 'parameter': 'q'}
            },
            {
                'type': 'sqli',
                'severity': 'High',
                'description': 'SQL syntax error detected indicating potential SQL injection vulnerability.',
                'url': 'http://demo-vulnerable.local/products.php?id=1',
                'evidence': 'SQL error: Syntax error in query after injection attempt',
                'details': {'payload': "' OR '1'='1", 'parameter': 'id', 'error': 'You have an error in your SQL syntax'}
            },
            {
                'type': 'csrf',
                'severity': 'Medium',
                'description': 'POST form missing CSRF token protection.',
                'url': 'http://demo-vulnerable.local/user/profile.php',
                'evidence': 'Form submits without anti-CSRF token field',
                'details': {'method': 'post', 'form_name': 'profile_update'}
            },
            {
                'type': 'xss',
                'severity': 'Medium',
                'description': 'DOM-based XSS vulnerability in user comment section.',
                'url': 'http://demo-vulnerable.local/comments.php?post=5',
                'evidence': 'User input rendered without sanitization',
                'details': {'payload': '<img src=x onerror=alert("xss")>', 'parameter': 'comment'}
            },
        ]
    }
    scan_history.insert(0, demo_result)
    return render_template('results.html', scan=demo_result)

@app.route('/about')
def about():
    return render_template('about.html')

def create_pdf_report(scan):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=48, bottomMargin=40)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.textColor = colors.HexColor('#1f2937')
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor('#0b3a60'))
    header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#0f4c75'))
    small_style = ParagraphStyle('Small', parent=styles['BodyText'], fontSize=10, leading=12, textColor=colors.HexColor('#334155'))

    story = []
    story.append(Paragraph('Web Vulnerability Scan Report', title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Target: {scan['target']}", normal))
    story.append(Paragraph(f"Scan time: {scan['scan_time']}", normal))
    story.append(Paragraph(f"Pages crawled: {scan['visited_pages']}", normal))
    story.append(Paragraph(f"Max pages: {scan['max_pages']}", normal))
    story.append(Spacer(1, 16))

    vuln_count = len(scan['vulnerabilities'])
    story.append(Paragraph(f"Total vulnerabilities found: {vuln_count}", header_style))
    story.append(Spacer(1, 12))

    table_data = [['Type', 'Severity', 'URL', 'Evidence', 'Details']]
    for vuln in scan['vulnerabilities']:
        details = str(vuln.get('details', ''))
        details = details.replace('\n', ' ').replace('  ', ' ')
        if len(details) > 180:
            details = details[:177] + '...'
        table_data.append([
            vuln['type'].upper(),
            vuln['severity'],
            vuln['url'],
            vuln['evidence'],
            details,
        ])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])

    vuln_table = Table(table_data, repeatRows=1, colWidths=[70, 70, 150, 130, 120])
    vuln_table.setStyle(table_style)
    story.append(vuln_table)
    story.append(Spacer(1, 24))
    story.append(Paragraph('Report generated by DarkScanner. Use this report for authorized security review and remediation tracking.', small_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
