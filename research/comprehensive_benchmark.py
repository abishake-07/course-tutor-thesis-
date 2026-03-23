"""
Comprehensive Defense Benchmark Runner
Tests all defense configurations and calculates metrics for RQ2.

Implements Defense E & F:
E. Re-run full benchmark for each configuration
F. Calculate ASR, mitigation rate, FPR for each
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from research.defense_configs import get_all_configs, get_config
from research.evaluate_datasets import DatasetEvaluator
from research.attack_analysis import AttackSuccessAnalyzer
from research.rubric_checker import RubricComplianceChecker


class ComprehensiveBenchmark:
    """Run comprehensive benchmark across all defense configurations."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.results = {}
        
    def save_config(self, defense_config: Dict):
        """Save defense configuration to config.yaml."""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        config['defenses'] = defense_config
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def run_single_configuration(self, config_name: str, config_obj) -> Dict:
        """Run benchmark for a single defense configuration."""
        print("\n" + "="*80)
        print(f"TESTING CONFIGURATION: {config_obj.name}")
        print(f"Description: {config_obj.description}")
        print("="*80)
        
        # Update config file
        self.save_config(config_obj.config)
        
        # Run evaluation
        evaluator = DatasetEvaluator(self.config_path)
        
        print("\n[1/4] Running benign queries...")
        benign_passed, benign_failed = evaluator.test_benign_queries()
        
        print("\n[2/4] Running attack queries...")
        attacks_blocked, attacks_bypassed = evaluator.test_attack_queries()
        
        print("\n[3/4] Generating evaluation report...")
        evaluator.generate_report(f"results/{config_name}_evaluation.json")
        
        print("\n[4/4] Analyzing attack success...")
        analyzer = AttackSuccessAnalyzer()
        attack_analysis = analyzer.analyze_evaluation_results(
            f"results/{config_name}_evaluation.json",
            f"results/{config_name}_attack_analysis.json"
        )
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            evaluator.results,
            attack_analysis,
            benign_passed,
            benign_failed,
            attacks_blocked,
            attacks_bypassed
        )
        
        return {
            "config": config_obj.config,
            "metrics": metrics,
            "evaluation": evaluator.results,
            "attack_analysis": attack_analysis
        }
    
    def _calculate_metrics(self, eval_results: Dict, attack_analysis: Dict,
                          benign_passed: int, benign_failed: int,
                          attacks_blocked: int, attacks_bypassed: int) -> Dict:
        """
        Calculate Defense F metrics:
        1. ASR (Attack Success Rate)
        2. Mitigation rate
        3. FPR (False Positive Rate)
        """
        total_attacks = attacks_blocked + attacks_bypassed
        total_benign = benign_passed + benign_failed
        
        asr = attack_analysis['asr_statistics']['overall_asr']
        detection_rate = (attacks_blocked / total_attacks * 100) if total_attacks > 0 else 0
        fpr = (benign_failed / total_benign * 100) if total_benign > 0 else 0
        
        return {
            "asr": asr,
            "detection_rate": detection_rate,
            "fpr": fpr,
            "attacks_total": total_attacks,
            "attacks_blocked": attacks_blocked,
            "attacks_bypassed": attacks_bypassed,
            "attacks_successful": attack_analysis['asr_statistics']['successful_attacks'],
            "benign_total": total_benign,
            "benign_passed": benign_passed,
            "benign_blocked": benign_failed,
            "by_category": attack_analysis['asr_statistics']['by_category']
        }
    
    def run_all_configurations(self, configs_to_test: List[str] = None):
        """
        Defense E: Run full benchmark for all configurations.
        
        Args:
            configs_to_test: List of config names to test, or None for all
        """
        all_configs = get_all_configs()
        
        if configs_to_test:
            configs = {k: v for k, v in all_configs.items() if k in configs_to_test}
        else:
            configs = all_configs
        
        print("\n" + "="*80)
        print(" "*20 + "COMPREHENSIVE DEFENSE BENCHMARK")
        print(" "*15 + f"Testing {len(configs)} configurations")
        print("="*80)
        
        baseline_asr = None
        
        for i, (config_name, config_obj) in enumerate(configs.items(), 1):
            print(f"\n\n>>> Configuration {i}/{len(configs)}: {config_name}")
            
            result = self.run_single_configuration(config_name, config_obj)
            self.results[config_name] = result
            
            # Store baseline ASR for mitigation calculation
            if config_name == "baseline":
                baseline_asr = result['metrics']['asr']
            elif baseline_asr is not None:
                # Calculate mitigation rate
                mitigation = baseline_asr - result['metrics']['asr']
                result['metrics']['mitigation_rate'] = mitigation
                result['metrics']['mitigation_percentage'] = (mitigation / baseline_asr * 100) if baseline_asr > 0 else 0
        
        # Generate comparison report
        self._generate_comparison_report()
    
    def _generate_comparison_report(self):
        """Generate comprehensive comparison report."""
        report_path = "results/comprehensive_benchmark_report.json"
        
        # Prepare summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "configurations_tested": len(self.results),
            "configuration_names": list(self.results.keys())
        }
        
        # Create comparison table data
        comparison = []
        for config_name, result in self.results.items():
            metrics = result['metrics']
            comparison.append({
                "configuration": config_name,
                "asr": metrics['asr'],
                "detection_rate": metrics['detection_rate'],
                "fpr": metrics['fpr'],
                "mitigation_rate": metrics.get('mitigation_rate', 0),
                "attacks_blocked": f"{metrics['attacks_blocked']}/{metrics['attacks_total']}",
                "benign_blocked": f"{metrics['benign_blocked']}/{metrics['benign_total']}"
            })
        
        # Full report
        report = {
            "summary": summary,
            "comparison_table": comparison,
            "detailed_results": self.results
        }
        
        # Save report
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self._print_comparison_summary(comparison)
        
        print(f"\n✓ Comprehensive benchmark report saved to: {report_path}")
    
    def _print_comparison_summary(self, comparison: List[Dict]):
        """Print formatted comparison table."""
        print("\n\n" + "="*100)
        print(" "*35 + "DEFENSE F: METRICS SUMMARY")
        print("="*100)
        
        # Header
        print(f"\n{'Configuration':<25} {'ASR':>8} {'Detection':>10} {'FPR':>8} {'Mitigation':>12} {'Blocked':>12}")
        print("-"*100)
        
        # Rows
        for row in comparison:
            config_name = row['configuration'][:24]
            asr = f"{row['asr']:.1f}%"
            detection = f"{row['detection_rate']:.1f}%"
            fpr = f"{row['fpr']:.1f}%"
            mitigation = f"{row['mitigation_rate']:.1f}%" if row['mitigation_rate'] != 0 else "baseline"
            blocked = row['attacks_blocked']
            
            print(f"{config_name:<25} {asr:>8} {detection:>10} {fpr:>8} {mitigation:>12} {blocked:>12}")
        
        print("="*100)
        
        # Find best configurations
        non_baseline = [r for r in comparison if r['configuration'] != 'baseline']
        if non_baseline:
            best_asr = min(non_baseline, key=lambda x: x['asr'])
            best_detection = max(non_baseline, key=lambda x: x['detection_rate'])
            lowest_fpr = min(comparison, key=lambda x: x['fpr'])
            
            print("\n🏆 BEST PERFORMERS:")
            print(f"  Lowest ASR:         {best_asr['configuration']} ({best_asr['asr']:.1f}%)")
            print(f"  Highest Detection:  {best_detection['configuration']} ({best_detection['detection_rate']:.1f}%)")
            print(f"  Lowest FPR:         {lowest_fpr['configuration']} ({lowest_fpr['fpr']:.1f}%)")
        
        print("\n" + "="*100)
        
        # RQ2 Answer
        print("\n📊 RQ2: WHICH DEFENSES ARE EFFECTIVE?")
        print("="*100)
        
        # Sort by detection rate
        sorted_by_detection = sorted(non_baseline, key=lambda x: x['detection_rate'], reverse=True)
        
        print("\nDefense Effectiveness Ranking (by Detection Rate):")
        for i, config in enumerate(sorted_by_detection[:5], 1):
            print(f"{i}. {config['configuration']}: {config['detection_rate']:.1f}% detection, "
                  f"{config['asr']:.1f}% ASR, {config['fpr']:.1f}% FPR")
        
        print("\n" + "="*100)


def main():
    """Run comprehensive benchmark."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run comprehensive defense benchmark')
    parser.add_argument('--configs', nargs='+', help='Specific configs to test (default: all)')
    parser.add_argument('--quick', action='store_true', help='Run quick test (baseline + full_defense only)')
    
    args = parser.parse_args()
    
    benchmark = ComprehensiveBenchmark()
    
    if args.quick:
        print("\n🚀 Running QUICK benchmark (baseline + full_defense only)")
        configs = ['baseline', 'full_defense']
    elif args.configs:
        configs = args.configs
    else:
        configs = None  # All configs
    
    benchmark.run_all_configurations(configs)
    
    print("\n\n" + "="*100)
    print(" "*30 + "BENCHMARK COMPLETE!")
    print("="*100)
    print("\n📁 Results saved in results/ directory")
    print("📊 View results/comprehensive_benchmark_report.json for full comparison")
    print("\n" + "="*100)


if __name__ == "__main__":
    main()
