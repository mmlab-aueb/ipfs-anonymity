"""
Script to save CID, PreviousCID, MultihashesCount, and all extracted Multihashes with parallel execution.
"""

import json
import os
import subprocess
import time
import re
from concurrent.futures import ThreadPoolExecutor

# Providers
providers = {
    "*****": {
        "peer_id": "*******",
        "address": "/****",
        "ads_file": "********.json",
    },
    "*****": {
        "peer_id": "*******",
        "address": "/*******",
        "ads_file": "******.json",
    },
    "******": {
        "peer_id": "*******",
        "address": "/*******",
        "ads_file": "******.json",
    },
}

def run_command(command):
    """Executes a shell command and returns the output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8"  # Ensure UTF-8 encoding
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(e.stderr)
        return None

def fetch_and_store_ads(provider_name, provider_info):
    """Fetch advertisement and store details and all extracted multihashes."""
    ads_file = provider_info["ads_file"]
    ads_data = load_json(ads_file)
    ads_data.setdefault("history", [])

    # Step 1: Fetch the latest advertisement
    command_ads = ["ipni", "ads", "get", "-ai=" + provider_info["address"], "--head"]
    output_ads = run_command(command_ads)
    if output_ads:
        cid = re.search(r"CID:\s*(\S+)", output_ads)
        previous_cid = re.search(r"PreviousCID:\s*(\S+)", output_ads)
        multihashes_count = re.search(r"Multihashes:\s*(\d+)", output_ads)

        if cid and previous_cid and multihashes_count:
            new_ad = {
                "CID": cid.group(1),
                "PreviousCID": previous_cid.group(1),
                "MultihashesCount": int(multihashes_count.group(1)),
                "Multihashes": []
            }

            # Step 2: Check if CID already exists
            existing_ad = next((ad for ad in ads_data["history"] if ad["CID"] == new_ad["CID"]), None)
            if existing_ad:
                # Compare MultihashesCount
                if existing_ad["MultihashesCount"] != new_ad["MultihashesCount"]:
                    print(f"Updating multihashes for CID {new_ad['CID']} due to count mismatch.")
                    # Fetch new multihashes
                    new_multihashes = fetch_multihashes(provider_info, new_ad["MultihashesCount"])
                    if new_multihashes:
                        existing_ad["MultihashesCount"] = new_ad["MultihashesCount"]
                        existing_ad["Multihashes"] = new_multihashes
                        save_json(ads_data, ads_file)
                        print(f"Updated advertisement for {provider_name}: {existing_ad}")
            else:
                # Fetch multihashes for new advertisement
                new_multihashes = fetch_multihashes(provider_info, new_ad["MultihashesCount"])
                if new_multihashes:
                    new_ad["Multihashes"] = new_multihashes
                ads_data["history"].append(new_ad)
                save_json(ads_data, ads_file)
                print(f"Stored new advertisement for {provider_name}: {new_ad}")
        else:
            print(f"Failed to extract required fields for {provider_name}.")
    else:
        print(f"Failed to fetch advertisement for {provider_name}.")

def fetch_multihashes(provider_info, multihashes_count):
    """Fetch all multihashes for the given count."""
    command_random = [
        "ipni",
        "random",
        "--pid=" + provider_info["peer_id"],
        "--number=1",
        f"--multihashes={multihashes_count}",
    ]
    output_random = run_command(command_random)
    if output_random:
        # Extract only valid multihashes using regex
        return re.findall(r"Qm[1-9A-HJ-NP-Za-km-z]{44}", output_random)
    else:
        print(f"Failed to fetch multihashes.")
        return []


def save_json(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {file_path}")

def load_json(file_path):
    """Load data from a JSON file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Error reading JSON file: {file_path}")
    return {}

def monitor_providers():
    """Monitor providers and fetch advertisements and multihashes periodically."""
    with ThreadPoolExecutor() as executor:
        while True:
            # Submit each provider's processing to the thread pool
            futures = [executor.submit(fetch_and_store_ads, name, info) for name, info in providers.items()]
            for future in futures:
                future.result()  # Wait for all tasks to complete

if __name__ == "__main__":
    monitor_providers()
