# Quick Start Guide - Running Defense Benchmarks

## Prerequisites
- Python 3.8+
- Required packages: `pyyaml`
- Both models (llama and phi-mini) running or accessible

## Installation
```bash
pip install pyyaml
```

## Running Benchmarks

### Option A: Attack Benchmarks (with Attacks)

Tests attacks against defense mechanisms to measure Attack Success Rate (ASR):

#### 1. **Quick Test** (5-10 minutes)
Tests only baseline and full_defense configurations:
```bash
python research/comprehensive_benchmark.py --model both --quick
```

#### 2. **Full Benchmark** (2-3 hours)
Tests all 11 defense configurations on both models:
```bash
python research/comprehensive_benchmark.py --model both
```

#### 3. **Single Model** (1-2 hours)
```bash
# Llama only
python research/comprehensive_benchmark.py --model llama

# Phi-mini only
python research/comprehensive_benchmark.py --model phi-mini
```

#### 4. **Specific Defenses**
```bash
python research/comprehensive_benchmark.py --model both --configs baseline full_defense recommended
```

---

### Option B: Benign-Only Benchmarks (NO Attacks)

Tests only legitimate queries to measure False Positive Rate (FPR) - determines if defenses incorrectly block legitimate student queries:

#### 1. **Quick Benign Test** (2-5 minutes)
Tests baseline and full_defense configurations:
```bash
python research/benign_benchmark.py --model both --quick
```

#### 2. **Full Benign Benchmark** (1-2 hours)
Tests all 11 defense configurations on both models with benign queries:
```bash
python research/benign_benchmark.py --model both
```

#### 3. **Single Model**
```bash
# Llama only
python research/benign_benchmark.py --model llama

# Phi-mini only
python research/benign_benchmark.py --model phi-mini
```

#### 4. **Specific Defenses**
```bash
python research/benign_benchmark.py --model both --configs baseline full_defense recommended
```

---

## Background Execution
To run without blocking your terminal:
```bash
python run_defense_benchmark.py
```

Monitor progress:
```bash
tail -f logs/defense_benchmark_*.log
```

## Output Location

Results are organized by model and defense category:

**Llama:**
- `results/llama/baseline/`
- `results/llama/structural/`
- `results/llama/detection_based/`
- `results/llama/processing/`
- `results/llama/comprehensive/`

**Phi-Mini:**
- `results/phi-mini/baseline/`
- `results/phi-mini/structural/`
- `results/phi-mini/detection_based/`
- `results/phi-mini/processing/`
- `results/phi-mini/comprehensive/`

## File Naming Convention

Timestamp format: `YYYYMMDD_HHMMSS`

### Attack Benchmarks:
- `{config_name}_attack_with_defense_20260428_112408.json`
- `{config_name}_attack_analysis_with_defense_20260428_112408.json`

### Benign Benchmarks:
- `{config_name}_benign_only_20260428_112408.json`
- Summary: `benign_benchmark_report_20260428_112408.json`

---

## Understanding the Results

### Attack Evaluation Report (`*_attack_with_defense_*.json`)
Contains:
- Benign test results (should pass)
- Attack test results (should be blocked)
- Defenses triggered
- Response snippets and full responses
- Overall statistics

### Benign Evaluation Report (`*_benign_only_*.json`)
Contains:
- Benign query results
- Whether each query was incorrectly blocked
- Defenses triggered
- False Positive Rate (FPR)

### Attack Analysis Report (`*_attack_analysis_with_defense_*.json`)
Contains:
- Attack Success Rate (ASR) - % of attacks that succeeded
- Category breakdown - ASR per attack category
- Failure modes analysis
- Outcome classification (proper_refusal, policy_bypass, ambiguous)

### Benchmark Reports
- **`comprehensive_benchmark_report_*.json`** - Attack metrics comparison
- **`benign_benchmark_report_*.json`** - FPR comparison

---

## Interpreting Metrics

### Attack Metrics
- **ASR (Attack Success Rate)**: % of attacks that bypassed defenses (lower is better)
- **Detection Rate**: % of attacks detected/blocked (higher is better)
- **FPR (False Positive Rate)**: % of benign queries blocked (lower is better)
- **Mitigation Rate**: Reduction in ASR vs baseline (higher is better)

### Benign Metrics
- **FPR (False Positive Rate)**: % of legitimate queries incorrectly blocked (lower is better)
- **Success Rate**: % of legitimate queries processed correctly (higher is better)

---

## Comparing Results

### Attack Benchmark:
```
Baseline (no defense):
  - ASR: 27%
  - FPR: 0%

Full Defense:
  - ASR: 5%
  - FPR: 5%
```

Interpretation: Full defense reduces attacks from 27% to 5% (80% mitigation) but blocks 5% of legitimate queries.

### Benign Benchmark:
```
Baseline:
  - FPR: 0% (no blocking)

Recommended Config:
  - FPR: 3% (blocks 3% of legitimate queries)
```

Interpretation: Recommended defense has minimal false positives (3%), still allows most legitimate queries.

---

## Best Practices

1. **Start with Quick Tests**
   ```bash
   python research/comprehensive_benchmark.py --model both --quick
   python research/benign_benchmark.py --model both --quick
   ```

2. **Check FPR First**
   - Run benign-only benchmark to ensure defenses don't block too many legitimate queries
   - Aim for FPR < 5%

3. **Then Check ASR**
   - Run full benchmark with attacks
   - Look for maximum ASR reduction with minimal FPR increase

4. **Analyze Results**
   - Compare `comprehensive_benchmark_report` with `benign_benchmark_report`
   - Identify trade-offs between security and usability

---

## Example Workflow

```bash
# 1. Quick benign test (check for false positives)
python research/benign_benchmark.py --model both --quick

# 2. Full benign test (comprehensive FPR analysis)
python research/benign_benchmark.py --model both

# 3. Quick attack test (verify defenses work)
python research/comprehensive_benchmark.py --model both --quick

# 4. Full attack test (comprehensive security analysis)
python research/comprehensive_benchmark.py --model both

# 5. Compare results
# - Check benign_benchmark_report_*.json for FPR
# - Check comprehensive_benchmark_report_*.json for ASR
```

---

## Troubleshooting

### Out of Memory
If the benchmark fails due to memory:
- Run with `--quick` first
- Run one model at a time instead of both

### Timeout Issues
If models are slow to respond:
- Run with specific configurations: `--configs baseline full_defense`
- Check model processes are running

### Missing Dependencies
```bash
pip install -r requirements.txt
```

---

## Support

For detailed setup information, see: `DEFENSE_BENCHMARK_SETUP.md`
