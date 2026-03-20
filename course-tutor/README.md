# Course Tutor Security Research System

A comprehensive framework for researching prompt injection attacks and defenses in an educational AI tutor context.

## Overview

This system implements a Data Science course tutor that can be tested against various prompt injection attacks and defended with configurable security mechanisms. It enables systematic research into the security-usability trade-offs in educational AI systems.

## Research Questions

**RQ1**: Which types of prompt-injection attacks (direct injection, indirect via PDFs, code-embedded instructions, multi-turn manipulation, and role-confusion attacks) can successfully compromise the data science course tutor to leak system prompts, provide unauthorized answers, or bypass grading policies?

**RQ2**: How effective are layered practical defenses (delimiter isolation, PDF sanitization, regex prompt-injection detection, trigger phrase detection, text normalization, and semantic risk scoring) in reducing successful attack rates while maintaining low false-positive rates?

**RQ3**: What trade-offs exist between defense stringency levels and pedagogical quality metrics (answer helpfulness, correctness of code feedback, conversation coherence, and student satisfaction ratings)?

## System Components

### Core System

- **`config.yaml`**: Configuration file for defenses, model settings, and system parameters
- **`core/pipeline.py`**: Main tutor pipeline handling conversations, PDFs, and code analysis
- **`core/defenses.py`**: Defense implementation and PDF extraction/sanitization utilities
- **`core/utils.py`**: System prompt text and rubric helpers
- **`app.py`**: Streamlit frontend for interactive tutoring and defense controls

### Security Components

- **`defenses.py`**: Implementation of defense mechanisms:
  - Delimiter isolation (XML-style content wrapping)
  - PDF sanitization (metadata and script removal)
    - Prompt injection detection (regex-based pattern matching)
    - Trigger phrase detection (fast phrase-level blocking)
    - Text normalization (light anti-obfuscation cleanup)
    - Semantic risk detection (weighted multi-signal scoring)

- **`attacks.py`**: Comprehensive attack scenario library (25+ attacks):
  - Direct prompt injection
  - Indirect injection via PDFs
  - Code-embedded instructions
  - Multi-turn manipulation
  - Role confusion attacks

### Evaluation & Logging

- **`logging_system.py`**: Comprehensive logging of all interactions, attacks, defenses, and feedback
- **`experiments.py`**: Experiment runner for systematic security testing
- **`evaluation.py`**: Pedagogical quality metrics and comparison tools

## Setup

### Prerequisites

```bash
# Install project dependencies
pip install -r requirements.txt
```

### Configuration

Edit `config.yaml` to configure:

1. **Defense settings**: Enable/disable specific defenses
2. **Model configuration**: Choose your LLM provider and settings
3. **Course details**: Customize for your course context
4. **Logging preferences**: Configure what gets logged

Current defense keys in `config.yaml`:

```yaml
defenses:
    enabled: true
    delimiter_isolation: true
    pdf_sanitization: true
    prompt_injection_detection: true
    trigger_phrase_detection: true
    text_normalization: true
    semantic_risk_detection: true
    semantic_block_threshold: 0.7
    semantic_review_threshold: 0.45
```

Notes:
- `semantic_block_threshold`: block when semantic score >= threshold.
- `semantic_review_threshold`: flag (but do not block) when semantic score >= threshold.

### LLM Integration

The system currently uses placeholder responses. To integrate a real LLM:

1. Open `pipeline.py`
2. Replace the `_generate_response()` method with your LLM API calls:

```python
def _generate_response(self, user_content: str) -> str:
    # Example with OpenAI
    import openai
    
    messages = self.conversation_history.get_messages_for_api()
    messages.append({"role": "user", "content": user_content})
    
    response = openai.ChatCompletion.create(
        model=self.config['model']['name'],
        messages=messages,
        temperature=self.config['model']['temperature'],
        max_tokens=self.config['model']['max_tokens']
    )
    
    return response.choices[0].message.content
```

## Usage

### Running the Tutor

```python
from pipeline import CourseTutor

# Initialize tutor
tutor = CourseTutor("config.yaml")

# Ask a question
response = tutor.process_message("Can you explain what pandas DataFrames are?")
print(response['response'])

# Submit code for review
code = """
import pandas as pd
def analyze_data(df):
    return df.describe()
"""
review = tutor.analyze_code(code, "Homework problem 2")
print(review['review'])

# Grade a submission
grading = tutor.grade_submission(submission_content, submission_type="pdf")
print(grading)
```

### Running Security Experiments

```python
from experiments import ExperimentRunner

# Initialize experiment runner
runner = ExperimentRunner()

# Test a specific defense configuration
defense_config = {
    "enabled": True,
    "delimiter_isolation": True,
    "pdf_sanitization": True,
    "prompt_injection_detection": True
}

results = runner.run_attack_experiment(
    defense_config=defense_config,
    experiment_name="all_defenses_test"
)

# Compare multiple defense configurations
defense_configs = [
    {"enabled": False, ...},  # Baseline
    {"enabled": True, "delimiter_isolation": True, ...},
    {"enabled": True, "prompt_injection_detection": True, ...},
    {"enabled": True, "delimiter_isolation": True, "pdf_sanitization": True, "prompt_injection_detection": True}
]

config_names = ["no_defenses", "delimiter_only", "detection_only", "all_defenses"]

comparison = runner.run_defense_comparison(defense_configs, config_names)
```

### Running the Comprehensive Benchmark

Use the benchmark runner to compare defense stacks on the same benign/attack datasets:

```bash
python research/comprehensive_benchmark.py --configs baseline regex_detection_only semantic_detection_only full_defense
```

Main output:
- `results/comprehensive_benchmark_report.json`

Latest snapshot (current code/config):

| Configuration | Detection Rate | False Positive Rate | Attacks Blocked |
|---|---:|---:|---:|
| baseline | 0.0% | 0.0% | 0/24 |
| regex_detection_only | 20.8% | 0.0% | 5/24 |
| semantic_detection_only | 8.3% | 0.0% | 2/24 |
| full_defense | 45.8% | 0.0% | 11/24 |

Interpretation:
- Best standalone detector on this dataset: regex detection.
- Best overall performance: full layered defense (defense-in-depth).

### Analyzing Results

```python
from logging_system import read_jsonl_logs, analyze_attack_logs

# Read attack logs
attacks = read_jsonl_logs("experiments/exp_20250101_120000/attack_test_attacks.jsonl")

# Analyze statistics
stats = analyze_attack_logs("experiments/exp_20250101_120000/attack_test_attacks.jsonl")
print(f"Detection Rate: {stats['detection_rate']:.2f}%")
print(f"Block Rate: {stats['block_rate']:.2f}%")

# Evaluate pedagogical quality
from evaluation import PedagogicalEvaluator

evaluator = PedagogicalEvaluator()
quality_metrics = evaluator.evaluate_batch(interactions)
print(f"Average Quality Score: {quality_metrics['aggregate_metrics']['avg_overall_quality']:.2f}")
```

## Attack Categories

### 1. Direct Prompt Injection (5 attacks)
- System prompt extraction
- Role override attempts
- Policy bypass
- Multi-step confusion
- Jailbreak attempts

### 2. Indirect Injection via PDF (3 attacks)
- Hidden instructions in white text/metadata
- JavaScript injection
- URL-encoded instructions

### 3. Code-Embedded Instructions (3 attacks)
- Instructions in code comments
- Instructions in string literals
- Docstring manipulation

### 4. Multi-Turn Manipulation (3 attacks)
- Gradual trust building
- Context injection via conversation history
- Emotional manipulation

### 5. Role Confusion (3 attacks)
- Nested roleplay scenarios
- Hypothetical framing
- Authority impersonation

### 6. Advanced Attacks (3 attacks)
- Prompt fragmentation
- Encoding bypass
- Logic bomb via conditionals

## Defense Mechanisms

### 1. Delimiter Isolation
Wraps user content in XML-style delimiters with explicit instructions to treat content as data, not instructions.

**Pros**: Simple, low overhead
**Cons**: Can be bypassed with sophisticated attacks

### 2. PDF Sanitization
Removes metadata, JavaScript, URLs, and suspicious patterns from PDF content.

**Pros**: Effective against indirect attacks
**Cons**: May remove legitimate content

### 3. Prompt Injection Detection
Uses regex patterns to detect common injection attempts.

**Pros**: Can block attacks before processing
**Cons**: False positives, can be evaded with novel patterns

### 4. Trigger Phrase Detection
Uses a lightweight phrase list for fast blocking of known jailbreak patterns.

**Pros**: Fast, easy to interpret
**Cons**: Evasion possible with paraphrasing

### 5. Text Normalization
Normalizes formatting and removes common obfuscation markers before downstream handling.

**Pros**: Improves consistency before detection/isolation
**Cons**: Can remove benign formatting context

### 6. Semantic Risk Detection
Computes a weighted score from intent-like signals (instruction override, prompt extraction, role reassignment, policy bypass, obfuscation cues, coercive urgency).

**Pros**: Captures broader attack intent than exact phrase matching
**Cons**: Requires threshold tuning by dataset

## Experimental Workflow

### Phase 1: Baseline Testing (No Defenses)
```python
runner.run_attack_experiment(
    defense_config={"enabled": False, ...},
    experiment_name="baseline"
)
```

### Phase 2: Individual Defense Testing
Test each defense mechanism separately:
```python
# Test delimiter isolation only
# Test PDF sanitization only
# Test prompt detection only
```

### Phase 3: Combined Defense Testing
Test all combinations:
```python
# Two defenses at a time
# All three defenses together
```

### Phase 4: Pedagogical Quality Assessment
For each configuration:
1. Run standard test questions
2. Measure response quality
3. Measure response time
4. Compare to baseline

### Phase 5: Analysis
```python
from evaluation import compare_pedagogical_quality

comparison = compare_pedagogical_quality(
    baseline_metrics,
    defense_metrics
)
print(f"Quality degradation: {comparison['overall_quality_loss']:.2f}%")
```

## Output Files

All experiments create structured output:

```
experiments/
  └── exp_YYYYMMDD_HHMMSS/
      ├── baseline_results.json
      ├── baseline_interactions.jsonl
      ├── baseline_attacks.jsonl
      ├── baseline_defenses.jsonl
      ├── baseline_feedback.jsonl
      ├── defense_comparison.json
      └── [other experiment results]
```

## Extending the System

### Adding New Attacks

Edit `attacks.py`:

```python
AttackScenario(
    id="NEW-001",
    name="Your Attack Name",
    category="your_category",
    description="Description of the attack",
    payload="The actual attack payload",
    expected_behavior="What should happen",
    success_criteria=["criterion1", "criterion2"]
)
```

### Adding New Defenses

Edit `defenses.py`:

```python
def _apply_your_defense(self, content: str) -> str:
    # Implement your defense
    return processed_content
```

Then integrate in `apply_defenses()` method.

### Customizing Evaluation

Edit `evaluation.py` to add custom quality metrics or evaluation criteria.

## Best Practices

1. **Always log everything**: Use the logging system extensively
2. **Run experiments systematically**: Test one variable at a time
3. **Use version control**: Track config changes for each experiment
4. **Document findings**: Add notes to experiment results
5. **Manual review**: Automated metrics are approximate; manually review samples

## Ethical Considerations

This system is for **research purposes only**. When deploying educational AI:

1. Prioritize student safety and privacy
2. Be transparent about AI limitations
3. Maintain human oversight for grading decisions
4. Regularly audit for biases and failures
5. Follow institutional IRB guidelines for educational research

## Citation

If you use this framework in your research, please cite:

```
[Your paper citation here]
```

## License

[Add your license here]

## Contact

[Add contact information for questions]
