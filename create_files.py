import os
import subprocess

# Parameters
gateways = ["****", "*******", "*******", "********"] #gateway URLs
intervals = ["1hour", "6hours", "12hours", "24hours"]
output_dir = "ipfs_test_files"

# Create directory for output files
os.makedirs(output_dir, exist_ok=True)

# Generate files and compute their CIDs
cids = {}
for gateway in gateways:
    for interval in intervals:
        file_name = f"{output_dir}/file_{gateway}_{interval}.txt"
        with open(file_name, "w") as file:
            file.write(f"This is a test file for {gateway} with interval {interval} #30 secs.\n")

        # Compute CID using `ipfs add`
        result = subprocess.run(["ipfs", "add", "-q", file_name], capture_output=True, text=True)
        cid = result.stdout.strip()
        cids[f"{gateway}_{interval}"] = cid
        print(f"File: {file_name}, CID: {cid}")

# Save CIDs to file
cid_file = "cids.txt"
with open(cid_file, "w") as f:
    for key, cid in cids.items():
        f.write(f"{key}: {cid}\n")
print(f"CIDs saved to {cid_file}")
