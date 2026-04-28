#!/usr/bin/env python
"""
Wrapper script to run the comprehensive defense benchmark
Logs output to a file for monitoring
"""

import subprocess
import sys
import os
from datetime import datetime

os.chdir(r"c:\Users\abish\OneDrive\Documents\Projects\course-tutor")

# Create logs directory
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"{log_dir}/defense_benchmark_{timestamp}.log"

print(f"Starting comprehensive defense benchmark...")
print(f"Output will be saved to: {log_file}")
print(f"Timestamp: {timestamp}\n")

# Run the benchmark
with open(log_file, 'w') as f:
    result = subprocess.run(
        [sys.executable, "research/comprehensive_benchmark.py", "--model", "both"],
        stdout=f,
        stderr=subprocess.STDOUT,
        text=True
    )

print(f"\nBenchmark completed with return code: {result.returncode}")
print(f"Results saved to:")
print(f"  - results/llama/[category]/")
print(f"  - results/phi-mini/[category]/")
print(f"\nLog file: {log_file}")
