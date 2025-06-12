import json
import hashlib
import cid

# Paths to input files
input_files = {
    "****": "******.json",
    "****": "******.json",
    "****": "******.json",
}

# Denylist file
denylist_file = "badbits.deny.txt"

def load_json(file_path):
    """Load a JSON file and return its content."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def load_denylist(file_path):
    """Load denylist hashes from a badbits-formatted file."""
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
        # Extract lines starting with `//` and strip the `//` prefix
        denylist = set(line.strip().lstrip("//") for line in lines if line.strip().startswith("//"))
        return {entry.lower() for entry in denylist}  # Normalize case
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return set()

def convert_to_cidv1(qm_hash):
    """Convert a Qm... CIDv0 hash to CIDv1 Base32."""
    try:
        c = cid.make_cid(qm_hash)
        c_v1 = c.to_v1()
        return c_v1.encode("base32").decode()
    except Exception as e:
        print(f"Error converting Qm hash {qm_hash} to CIDv1: {e}")
        return None

def compute_denylist_hash(cidv1_base32):
    """Compute the sha256 hash of <cid_v1>/."""
    try:
        cid_with_slash = f"{cidv1_base32}/"
        return hashlib.sha256(cid_with_slash.encode()).hexdigest()
    except Exception as e:
        print(f"Error computing denylist hash for {cidv1_base32}: {e}")
        return None

def count_denylist_matches(input_files, denylist):
    """Count how many multihashes from each file are in the denylist."""
    results = {}
    for provider, file_path in input_files.items():
        print(f"Processing {provider} from {file_path}...")
        data = load_json(file_path)
        if not data:
            results[provider] = {
                "Total Multihashes": 0,
                "In Denylist": 0,
                "Matching Multihashes": [],
            }
            continue

        # Extract all multihashes
        all_multihashes = set()
        for ad in data.get("history", []):
            all_multihashes.update(ad.get("Multihashes", []))

        # Check against denylist
        denylist_matches = []
        for mh in all_multihashes:
            cidv1 = convert_to_cidv1(mh)
            if not cidv1:
                continue

            denylist_hash = compute_denylist_hash(cidv1)
            if denylist_hash in denylist:
                denylist_matches.append(mh)

        results[provider] = {
            "Total Multihashes": len(all_multihashes),
            "In Denylist": len(denylist_matches),
            "Matching Multihashes": denylist_matches,
        }

    return results

def main():
    # Load denylist
    denylist = load_denylist(denylist_file)
    print(f"Loaded {len(denylist)} denylist entries.")

    # Count matches for each file
    results = count_denylist_matches(input_files, denylist)

    # Print results
    print("\nResults:")
    for provider, counts in results.items():
        print(f"{provider}:")
        print(f"  Total Multihashes: {counts['Total Multihashes']}")
        print(f"  In Denylist: {counts['In Denylist']}")
        if counts["Matching Multihashes"]:
            print(f"  Matching Multihashes:")
            for mh in counts["Matching Multihashes"]:
                print(f"    {mh}")

if __name__ == "__main__":
    main()
