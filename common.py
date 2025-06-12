import json
from collections import defaultdict
import base58

# Paths to JSON files for each provider
json_files = {
    "*****": "*******.json", #gateway_name : gateway_name.json
    "*****": "******.json",
    "*****": "******.json",
}

output_file = "common_multihashes_with_digests.json"

def load_multihashes(file_path):
    """Load multihashes from a provider's JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            multihashes = set()
            for ad in data.get("history", []):
                multihashes.update(ad.get("Multihashes", []))
            return multihashes
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return set()

def decode_multihash(mh):
    """Decode a Base58-encoded multihash and extract its digest."""
    raw = base58.b58decode(mh)
    hash_function_code = raw[0]
    digest_length = raw[1]
    digest = raw[2:]
    return {
        "hash_function_code": hash_function_code,
        "digest_length": digest_length,
        "digest": digest.hex(),
    }

def find_common_multihashes(json_files):
    """Find common multihashes among providers."""
    provider_multihashes = {}
    all_multihashes = defaultdict(set)

    # Load multihashes for each provider
    for provider, file_path in json_files.items():
        print(f"Loading multihashes for {provider} from {file_path}...")
        provider_multihashes[provider] = load_multihashes(file_path)

        # Add multihashes with their respective provider
        for mh in provider_multihashes[provider]:
            all_multihashes[mh].add(provider)

    # Filter out multihashes found in only one provider
    common_multihashes = [
        {
            "multihash": mh,
            "digest": decode_multihash(mh)["digest"],
            "providers": list(providers),
        }
        for mh, providers in all_multihashes.items()
        if len(providers) > 1  # Only include those shared by at least 2 providers
    ]

    return common_multihashes

def save_results_to_file(common_multihashes, output_file):
    """Save the common multihashes and their digests to a file."""
    with open(output_file, "w") as file:
        json.dump(common_multihashes, file, indent=4)
    print(f"Results saved to {output_file}")

def main():
    """Main function to compare multihashes."""
    common_multihashes = find_common_multihashes(json_files)

    # Display the summary count
    print(f"\nNumber of common multihashes (shared by at least 2 providers): {len(common_multihashes)}")

    # Save results to a file
    save_results_to_file(common_multihashes, output_file)

if __name__ == "__main__":
    main()
