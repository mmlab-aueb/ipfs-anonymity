# IPFS/IPNI Analysis Tools

This repository contains a collection of Python scripts used for experimental analysis in the context of the following academic publication:

📄 **[Hello, won't you tell me your name?: Investigating Anonymity Abuse in IPFS](https://arxiv.org/abs/2506.04307)**  
*arXiv preprint, June 2025*

## ⚠️ Disclaimer

This is **academic code** developed specifically for the experiments described in the above paper.  
It is not production-grade software and may contain bugs, assumptions, or simplifications that are acceptable in an experimental setting.

We welcome feedback, but use the code at your own risk.

---

## 🧩 Contents

### IPNI Advertisement Tools

- `ipni_monitor.py`  
  Continuously monitors new advertisements from a specific IPNI publisher and extracts metadata (CID, multihash count, linkage).

### Random Advertisement Collection

- `random.py`  
  Collects random advertisements from IPNI using the `ipni random` command, saving multihash lists and statistics.

### Gateway Availability Probing

- `create_files.py`  
  Generates test files and publishes them to IPFS to compute their CIDs.
  
- `gateway_availability_check.py`  
  Periodically checks if each CID is reachable from public gateways (e.g., ipfs.io).

### Multihash Comparison and Policy Matching

- `common.py`  
  Identifies multihashes that appear in two or more storage providers.

- `district_deny.py`  
  Checks multihashes against a denylist file in [badbits][https://badbits.dwebops.pub/badbits.deny] format.

---

## 💻 Requirements

- Python 3.8+
- IPFS daemon and CLI (`ipfs add`)
- IPNI CLI (`ipni`)
- Install Python dependencies:

```bash
pip install -r requirements.txt
