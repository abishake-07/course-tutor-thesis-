"""
Evaluation script for testing course tutor with controlled datasets.
Tests both benign queries (should pass) and attack queries (should be blocked).
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import CourseTutor, DefenseManager, TutorLogger
import yaml
from research.evaluation import PedagogicalEvaluator


class DatasetEvaluator:
    """Evaluates course tutor performance on benign and attack datasets."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize evaluator with configuration."""
        self.config_path = config_path
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.tutor = CourseTutor(config_path)
        self.quality_evaluator = PedagogicalEvaluator()
        self.results = {
            'benign_tests': [],
            'attack_tests': [],
            'summary': {}
        }

    @staticmethod
    def _latency_stats(values: List[float]) -> Dict[str, float]:
        """Compute stable latency summary stats for reporting."""
        if not values:
            return {
                'count': 0,
                'mean_seconds': 0.0,
                'p50_seconds': 0.0,
                'p95_seconds': 0.0,
                'max_seconds': 0.0
            }

        vals = sorted(float(v) for v in values)
        n = len(vals)

        def pct(p: float) -> float:
            if n == 1:
                return vals[0]
            idx = int(round((n - 1) * p))
            return vals[idx]

        return {
            'count': n,
            'mean_seconds': sum(vals) / n,
            'p50_seconds': pct(0.50),
            'p95_seconds': pct(0.95),
            'max_seconds': vals[-1]
        }
    
    def load_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Load dataset from JSON file."""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_benign_queries(self, dataset_path: str = "datasets/benign_queries.json"):
        """Test system with benign student queries."""
        print("\n" + "="*70)
        print("TESTING BENIGN QUERIES")
        print("="*70)
        
        dataset = self.load_dataset(dataset_path)
        queries = dataset['queries']
        
        passed = 0
        failed = 0
        
        for query_obj in queries:
            query_id = query_obj['id']
            query = query_obj['query']
            category = query_obj['category']
            
            print(f"\n[{query_id}] Category: {category}")
            print(f"Query: {query[:80]}..." if len(query) > 80 else f"Query: {query}")
            
            try:
                start_time = time.perf_counter()
                result_dict = self.tutor.process_message(query)
                elapsed_seconds = time.perf_counter() - start_time
                response = result_dict['response']
                blocked = result_dict['blocked']
                defense_log = result_dict['defense_log']
                
                # Extract triggered defenses from log
                triggered = defense_log.get('defenses_applied', [])
                threats = defense_log.get('threats_detected', [])
                
                # Benign queries should NOT be blocked
                if blocked:
                    print("❌ FAILED: Benign query was blocked by defenses")
                    failed += 1
                    result = 'false_positive'
                else:
                    print("✅ PASSED: Query processed successfully")
                    passed += 1
                    result = 'success'

                quality_metrics = self.quality_evaluator.evaluate_response(
                    question=query,
                    response=response,
                    response_time=elapsed_seconds
                )
                
                self.results['benign_tests'].append({
                    'id': query_id,
                    'category': category,
                    'query': query,
                    'result': result,
                    'blocked': blocked,
                    'defenses_triggered': triggered,
                    'response_time_seconds': elapsed_seconds,
                    'quality_metrics': {
                        'helpfulness_score': quality_metrics.helpfulness_score,
                        'correctness_score': quality_metrics.correctness_score,
                        'coherence_score': quality_metrics.coherence_score,
                        'learning_support_score': quality_metrics.learning_support_score,
                        'overall_score': quality_metrics.overall_score()
                    },
                    'response_length': len(response),
                    'full_response': response  # Store for rubric compliance checking
                })
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                failed += 1
                self.results['benign_tests'].append({
                    'id': query_id,
                    'category': category,
                    'query': query,
                    'result': 'error',
                    'response_time_seconds': 0.0,
                    'error': str(e)
                })
        
        print(f"\n{'='*70}")
        print(f"Benign Queries: {passed} passed, {failed} failed (Total: {len(queries)})")
        print(f"False Positive Rate: {(failed/len(queries)*100):.1f}%")
        print(f"{'='*70}")
        
        return passed, failed
    
    def test_attack_queries(self, dataset_path: str = "datasets/attack_queries.json"):
        """Test system with malicious attack queries."""
        print("\n" + "="*70)
        print("TESTING ATTACK QUERIES")
        print("="*70)
        
        dataset = self.load_dataset(dataset_path)
        attacks = dataset['attacks']
        
        blocked = 0
        bypassed = 0
        
        category_stats = {}
        
        for attack_obj in attacks:
            attack_id = attack_obj['id']
            query = attack_obj['query']
            category = attack_obj['category']
            attack_goal = attack_obj['attack_goal']
            severity = attack_obj['severity']
            expected_detection = attack_obj.get('expected_detection', True)
            
            if category not in category_stats:
                category_stats[category] = {'blocked': 0, 'bypassed': 0}
            
            print(f"\n[{attack_id}] {category} - {severity.upper()}")
            print(f"Goal: {attack_goal}")
            print(f"Query: {query[:80]}..." if len(query) > 80 else f"Query: {query}")
            
            try:
                start_time = time.perf_counter()
                result_dict = self.tutor.process_message(query)
                elapsed_seconds = time.perf_counter() - start_time
                response = result_dict['response']
                is_blocked = result_dict['blocked']
                defense_log = result_dict['defense_log']
                
                # Extract triggered defenses from log
                triggered = defense_log.get('defenses_applied', [])
                threats = defense_log.get('threats_detected', [])
                
                # Attacks should be blocked
                if is_blocked:
                    print(f"✅ BLOCKED by: {', '.join(triggered)}")
                    blocked += 1
                    category_stats[category]['blocked'] += 1
                    result = 'blocked'
                else:
                    print("⚠️  BYPASSED: Attack was not detected")
                    if not expected_detection:
                        print("   (Expected - advanced attack)")
                    bypassed += 1
                    category_stats[category]['bypassed'] += 1
                    result = 'bypassed'
                
                self.results['attack_tests'].append({
                    'id': attack_id,
                    'category': category,
                    'severity': severity,
                    'attack_goal': attack_goal,
                    'query': query,
                    'result': result,
                    'blocked': is_blocked,
                    'defenses_triggered': triggered,
                    'expected_detection': expected_detection,
                    'response_time_seconds': elapsed_seconds,
                    'response_snippet': response[:150],
                    'full_response': response  # Store full response for analysis
                })
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                self.results['attack_tests'].append({
                    'id': attack_id,
                    'category': category,
                    'result': 'error',
                    'response_time_seconds': 0.0,
                    'error': str(e)
                })
        
        print(f"\n{'='*70}")
        print(f"Attack Queries: {blocked} blocked, {bypassed} bypassed (Total: {len(attacks)})")
        print(f"Detection Rate: {(blocked/len(attacks)*100):.1f}%")
        print(f"\nDetection by Category:")
        for cat, stats in category_stats.items():
            total = stats['blocked'] + stats['bypassed']
            rate = (stats['blocked']/total*100) if total > 0 else 0
            print(f"  {cat:25s}: {stats['blocked']:2d}/{total:2d} blocked ({rate:5.1f}%)")
        print(f"{'='*70}")
        
        return blocked, bypassed
    
    def generate_report(self, output_path: str = "results/evaluation_report.json"):
        """Generate detailed evaluation report."""
        
        # Calculate summary statistics
        benign_total = len(self.results['benign_tests'])
        benign_passed = sum(1 for t in self.results['benign_tests'] if t.get('result') == 'success')
        benign_failed = benign_total - benign_passed
        
        attack_total = len(self.results['attack_tests'])
        attack_blocked = sum(1 for t in self.results['attack_tests'] if t.get('result') == 'blocked')
        attack_bypassed = attack_total - attack_blocked

        benign_latencies = [
            t.get('response_time_seconds', 0.0)
            for t in self.results['benign_tests']
            if t.get('result') in {'success', 'false_positive'}
        ]
        attack_latencies = [
            t.get('response_time_seconds', 0.0)
            for t in self.results['attack_tests']
            if t.get('result') in {'blocked', 'bypassed'}
        ]
        all_latencies = benign_latencies + attack_latencies

        quality_interactions = [
            {
                'question': t['query'],
                'response': t.get('full_response', ''),
                'response_time_seconds': t.get('response_time_seconds', 0.0)
            }
            for t in self.results['benign_tests']
            if t.get('result') in {'success', 'false_positive'} and t.get('full_response')
        ]
        quality_summary = self.quality_evaluator.evaluate_batch(quality_interactions)
        
        self.results['summary'] = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'model': self.config['model']['name'],
                'provider': self.config['model']['provider'],
                'defenses': self.config['defenses']
            },
            'benign_queries': {
                'total': benign_total,
                'passed': benign_passed,
                'false_positives': benign_failed,
                'false_positive_rate': (benign_failed/benign_total*100) if benign_total > 0 else 0
            },
            'attack_queries': {
                'total': attack_total,
                'blocked': attack_blocked,
                'bypassed': attack_bypassed,
                'detection_rate': (attack_blocked/attack_total*100) if attack_total > 0 else 0
            },
            'latency': {
                'benign': self._latency_stats(benign_latencies),
                'attack': self._latency_stats(attack_latencies),
                'overall': self._latency_stats(all_latencies)
            },
            'quality_metrics': quality_summary.get('aggregate_metrics', {}),
            'overall_accuracy': {
                'correct': benign_passed + attack_blocked,
                'incorrect': benign_failed + attack_bypassed,
                'total': benign_total + attack_total,
                'accuracy': ((benign_passed + attack_blocked)/(benign_total + attack_total)*100) 
                           if (benign_total + attack_total) > 0 else 0
            }
        }
        
        # Save report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print("EVALUATION SUMMARY")
        print(f"{'='*70}")
        print(f"\nBenign Queries:")
        print(f"  Total: {benign_total}")
        print(f"  Passed: {benign_passed} ({benign_passed/benign_total*100:.1f}%)")
        print(f"  False Positives: {benign_failed} ({self.results['summary']['benign_queries']['false_positive_rate']:.1f}%)")
        print(f"\nAttack Queries:")
        print(f"  Total: {attack_total}")
        print(f"  Blocked: {attack_blocked} ({self.results['summary']['attack_queries']['detection_rate']:.1f}%)")
        print(f"  Bypassed: {attack_bypassed}")
        print(f"\nOverall Performance:")
        print(f"  Accuracy: {self.results['summary']['overall_accuracy']['accuracy']:.1f}%")
        print(f"  ({self.results['summary']['overall_accuracy']['correct']}/{self.results['summary']['overall_accuracy']['total']} correct)")
        latency = self.results['summary']['latency']['overall']
        print(f"\nLatency (Overall):")
        print(f"  Mean: {latency['mean_seconds']:.3f}s | p50: {latency['p50_seconds']:.3f}s | p95: {latency['p95_seconds']:.3f}s")
        quality = self.results['summary'].get('quality_metrics', {})
        if quality:
            print(f"\nQuality (Benign Queries):")
            print(f"  Helpfulness: {quality.get('avg_helpfulness', 0.0):.2f} | Correctness: {quality.get('avg_correctness', 0.0):.2f}")
            print(f"  Coherence: {quality.get('avg_coherence', 0.0):.2f} | Learning Support: {quality.get('avg_learning_support', 0.0):.2f}")
            print(f"  Overall Quality: {quality.get('avg_overall_quality', 0.0):.2f}")
        print(f"\nDetailed report saved to: {output_path}")
        print(f"{'='*70}\n")
    
    def run_full_evaluation(self):
        """Run complete evaluation on both datasets."""
        print("\n" + "="*70)
        print("COURSE TUTOR SECURITY EVALUATION")
        print(f"Model: {self.config['model']['name']} ({self.config['model']['provider']})")
        print(f"Defenses: {', '.join([k for k, v in self.config['defenses'].items() if v])}")
        print("="*70)
        
        # Test benign queries
        self.test_benign_queries()
        
        # Test attack queries
        self.test_attack_queries()
        
        # Generate report
        self.generate_report()


def main():
    """Main evaluation function."""
    evaluator = DatasetEvaluator()
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()
