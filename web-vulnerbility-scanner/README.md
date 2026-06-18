# Web Vulnerability Scanner

A Python Flask web interface for scanning websites for common vulnerabilities including XSS, SQL injection, and CSRF.

## Setup

1. Create a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

4. Open `http://127.0.0.1:5000` in your browser.

## Usage

- Enter a target URL.
- Optionally set maximum pages to crawl.
- Review scan results and evidence in the web UI.
- Download a professional PDF report from the results page.

## Notes

- This scanner is for educational and authorized testing only.
- Always obtain permission before scanning live targets.
