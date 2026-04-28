# Defense Benchmark Setup - Complete

## Overview
Updated the `comprehensive_benchmark.py` script to run all defense mechanisms against attacks on both models with proper timestamping and organization.

## Changes Made

### 1. **Dynamic Timestamp Generation**
- Added `datetime` import to generate timestamps: `YYYYMMDD_HHMMSS`
- Timestamp is created when ComprehensiveBenchmark is initialized
- All output files include this timestamp

### 2. **Defense Category Organization**
Defenses are now categorized:
- **baseline**: No defenses (control group)
- **structural**: Delimiter-based isolation
  - delimiter_only
  - delimiter_pdf
- **processing**: Text/content sanitization
  - normalization_only
  - pdf_sanitization_only
- **detection_based**: Pattern and semantic detection
  - regex_detection_only
  - trigger_detection_only
  - semantic_detection_only
  - all_detection
- **comprehensive**: Full defense stacks
  - full_defense
  - recommended

### 3. **Output File Structure**
Files are now organized as:
```
results/
  ├── llama/
  │   ├── baseline/
  │   │   └── baseline_attack_with_defense_20260428_112408.json
  │   ├── structural/
  │   │   ├── delimiter_only_attack_with_defense_20260428_112408.json
  │   │   └── delimiter_pdf_attack_with_defense_20260428_112408.json
  │   ├── detection_based/
  │   ├── processing/
  │   ├── comprehensive/
  │   └── comprehensive_benchmark_report_20260428_112408.json
  │
  └── phi-mini/
      ├── baseline/
      ├── structural/
      ├── detection_based/
      ├── processing/
      ├── comprehensive/
      └── comprehensive_benchmark_report_20260428_112408.json
```

### 4. **Filename Format**
- `{config_name}_attack_with_defense_{timestamp}.json` - Main evaluation report
- `{config_name}_attack_analysis_with_defense_{timestamp}.json` - Attack analysis
- `comprehensive_benchmark_report_{timestamp}.json` - Summary report

### 5. **Model Parameter**
Updated to accept model selection:
- `--model llama` - Test only Llama
- `--model phi-mini` - Test only Phi-Mini
- `--model both` (default) - Test both models

### 6. **Command-Line Options**
```bash
# Test all defenses on both models
python research/comprehensive_benchmark.py --model both

# Test all defenses on one model
python research/comprehensive_benchmark.py --model llama

# Quick test (baseline + full_defense only)
python research/comprehensive_benchmark.py --model both --quick

# Test specific configurations
python research/comprehensive_benchmark.py --model both --configs baseline full_defense recommended
```

## Running the Benchmark

### Option 1: Direct Execution (blocking)
```bash
cd c:\Users\abish\OneDrive\Documents\Projects\course-tutor
python research/comprehensive_benchmark.py --model both
```

### Option 2: Background Execution (recommended)
```bash
python run_defense_benchmark.py
```
This will:
- Run the benchmark in the background
- Log all output to `logs/defense_benchmark_{timestamp}.log`
- Display the results directory structure

## What Gets Generated

For each defense configuration tested, the script generates:

1. **Attack Evaluation Report** (`*_attack_with_defense_*.json`)
   - Benign query tests
   - Attack query tests
   - Defenses triggered
   - Overall statistics

2. **Attack Analysis** (`*_attack_analysis_with_defense_*.json`)
   - Attack success rate (ASR)
   - Categorized attack analysis
   - Failure modes
   - Outcome distribution

3. **Benchmark Report** (`comprehensive_benchmark_report_*.json`)
   - Summary of all configurations tested
   - Metrics comparison (ASR, detection rate, FPR)
   - Best performers by category
   - Mitigation rates

## Expected Results Location

After running:
```
results/
├── llama/
│   ├── baseline/
│   ├── structural/
│   ├── processing/
│   ├── detection_based/
│   ├── comprehensive/
│   └── comprehensive_benchmark_report_20260428_*.json
│
└── phi-mini/
    ├── baseline/
    ├── structural/
    ├── processing/
    ├── detection_based/
    ├── comprehensive/
    └── comprehensive_benchmark_report_20260428_*.json
```

## Notes

- Each run creates a unique timestamp, allowing multiple runs to be tracked
- Defense categories help organize and analyze which types of defenses are most effective
- The full benchmark tests all 11 defense configurations on both models (22 test runs total)
- Each model evaluation takes ~5-15 minutes per configuration depending on the models' response time
