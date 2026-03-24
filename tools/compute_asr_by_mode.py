"""Compute ASR by failure-mode and category.

Reads `results/attack_success_analysis.json` (output from research/attack_analysis.py)
and writes `results/asr_by_failure_mode.json` with per-mode and category×mode matrices.
"""
import json
from pathlib import Path
from collections import defaultdict


def load_analysis(path="results/attack_success_analysis.json"):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_asr_by_mode(analysis):
    attacks = analysis.get('attack_analyses', [])

    mode_counts = defaultdict(lambda: {'attempts': 0, 'successes': 0})
    cat_mode = defaultdict(lambda: defaultdict(lambda: {'attempts': 0, 'successes': 0}))

    for a in attacks:
        category = a.get('attack_category', 'unknown')
        success = a.get('attack_succeeded', False)
        modes = a.get('failure_modes') or []

        # If no explicit modes, fall back to outcome type
        if not modes and a.get('outcome_type'):
            modes = [a.get('outcome_type')]

        # Count per mode
        for m in set(modes):
            mode_counts[m]['attempts'] += 1
            if success:
                mode_counts[m]['successes'] += 1

            cat_mode[category][m]['attempts'] += 1
            if success:
                cat_mode[category][m]['successes'] += 1

    # Convert to percentages
    mode_stats = {}
    for m, stats in mode_counts.items():
        attempts = stats['attempts']
        successes = stats['successes']
        mode_stats[m] = {
            'attempts': attempts,
            'successes': successes,
            'asr_percent': (successes / attempts * 100) if attempts > 0 else 0.0
        }

    category_mode_stats = {}
    for cat, modes in cat_mode.items():
        category_mode_stats[cat] = {}
        for m, stats in modes.items():
            attempts = stats['attempts']
            successes = stats['successes']
            category_mode_stats[cat][m] = {
                'attempts': attempts,
                'successes': successes,
                'asr_percent': (successes / attempts * 100) if attempts > 0 else 0.0
            }

    return {
        'mode_stats': mode_stats,
        'category_mode_stats': category_mode_stats
    }


def main():
    Path('results').mkdir(parents=True, exist_ok=True)

    analysis = load_analysis()
    stats = compute_asr_by_mode(analysis)

    out_path = Path('results') / 'asr_by_failure_mode.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'metadata': analysis.get('metadata', {}), 'asr_by_mode': stats}, f, indent=2)

    print(f"Wrote ASR by failure mode to {out_path}")


if __name__ == '__main__':
    main()
