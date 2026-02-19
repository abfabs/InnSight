#!/usr/bin/env python3
"""
Run all aggregate jobs in sequence.

Usage:
    python backend/scripts/run_aggregates.py
"""

import os
import sys
import time
from datetime import datetime
import importlib

# Make backend root importable
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
sys.path.insert(0, BACKEND_ROOT)


MODULES = [
    ("Occupancy by month", "scripts.aggregate_occupancy"),
    ("Room type distribution", "scripts.aggregate_room_types"),
    ("Sentiment summary", "scripts.aggregate_sentiment"),
    ("Top hosts", "scripts.aggregate_top_hosts"),
]


def banner(msg: str):
    print("\n" + "=" * 70)
    print(msg)
    print("=" * 70)


def run_step(label: str, module_path: str):
    banner(f"▶ Running: {label}")
    start = time.time()

    module = importlib.import_module(module_path)

    if not hasattr(module, "main"):
        raise RuntimeError(f"{module_path} has no main() function")

    result = module.main()

    if result is False:
        raise RuntimeError(f"{label} returned False")

    duration = time.time() - start
    print(f"✅ Finished: {label} ({duration:.2f}s)")


def main():
    overall_start = datetime.now()
    banner(f"🚀 Starting Aggregates @ {overall_start}")

    for label, module_path in MODULES:
        run_step(label, module_path)

    overall_end = datetime.now()
    banner("🎉 ALL AGGREGATES COMPLETED")
    print(f"Started : {overall_start}")
    print(f"Finished: {overall_end}")
    print(f"Total   : {(overall_end - overall_start)}")


if __name__ == "__main__":
    main()
