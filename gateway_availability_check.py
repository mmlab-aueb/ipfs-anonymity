import requests
import time
from datetime import datetime

# Load CIDs from file
cid_file = "cids.txt"
base_urls = {
    "*****": "*******", #format: "name" : URL
    "*****": "*******",
    "*****": "*******",
    "*****": "*******"
}

cids = {}
with open(cid_file, "r") as f:
    for line in f:
        key, cid = line.strip().split(": ")
        cids[key] = cid

# Create URLs and check intervals
files = {key: f"{base_urls[key.split('_')[0]]}{cid}" for key, cid in cids.items()}
check_intervals = {
    "5mins": 300,
    "1hour": 3600,
    "6hours": 21600,
    "12hours": 43200,
    "24hours": 86400,
}

log_files = {key: f"cache_status_{key}.txt" for key in files.keys()}

# Function to check availability

def check_file_availability(url, log_file):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }
        response = requests.head(url, timeout=30, verify=False, allow_redirects=True, headers=headers)
        status_code = response.status_code
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a") as log:
            if status_code == 200:
                log.write(f"[{timestamp}] File is available: {url}\n")
                print(f"[{timestamp}] File is available: {url}")
            else:
                log.write(f"[{timestamp}] File NOT available (status {status_code}): {url}\n")
                print(f"[{timestamp}] File NOT available (status {status_code}): {url}")
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as log:
            log.write(f"[{timestamp}] Error: {str(e)}\n")
        print(f"[{timestamp}] Error: {str(e)}")

# Periodic Checking
next_check = {key: time.time() for key in files.keys()}  # Timer for each interval

while True:
    current_time = time.time()
    for key, url in files.items():
        scenario = key.split('_')[1]
        if current_time >= next_check[key]:
            check_file_availability(url, log_files[key])
            next_check[key] = current_time + check_intervals[scenario]
    time.sleep(60)  # Short delay to avoid tight loop
