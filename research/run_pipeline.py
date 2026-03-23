"""
Comprehensive Security Research Pipeline
Implements the complete evaluation workflow for RQ1 and thesis methodology.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from research.evaluate_datasets import DatasetEvaluator
from research.attack_analysis import AttackSuccessAnalyzer
from research.rubric_checker import RubricComplianceChecker


class ResearchPipeline:
    """Complete research pipeline for security evaluation."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize pipeline."""
        self.config_path = config_path
        self.evaluator = DatasetEvaluator(config_path)
        self.attack_analyzer = AttackSuccessAnalyzer()
        self.rubric_checker = RubricComplianceChecker()
    
    def run_baseline_evaluation(self):
        """
        Step 1-2: Run benign and attack queries through baseline (no defenses).
        
        This implements:
        - Run all benign queries through pipeline with no defenses
        - Check that behavior is normal
        - Run all attacked queries through same baseline
        - Store all outputs
        """
        print("\n" + "="*70)
        print("STEP 1-2: BASELINE EVALUATION (NO DEFENSES)")
        print("="*70)
        print("\nRunning benign and attack queries through unprotected system...")
        
        # Run full evaluation
        self.evaluator.run_full_evaluation()
        
        print("\n✓ Baseline evaluation complete!")
        print("  - Benign queries tested for normal behavior")
        print("  - Attack queries tested for vulnerabilities")
        print("  - All outputs stored in results/evaluation_report.json")
    
    def analyze_attack_success(self):
        """
        Step 3-4: Analyze attack success and calculate ASR.
        
        This implements:
        - For each attacked item, decide if attack was successful
        - Define clear success conditions (solution leakage, etc.)
        - Calculate Attack Success Rate (ASR)
        - Break down ASR by attack type
        """
        print("\n" + "="*70)
        print("STEP 3-4: ATTACK SUCCESS ANALYSIS")
        print("="*70)
        print("\nAnalyzing attack outcomes and calculating ASR...")
        
        # Analyze attacks
        self.attack_analyzer.analyze_evaluation_results(
            eval_report_path="results/evaluation_report.json",
            output_path="results/attack_success_analysis.json"
        )
        
        print("\n✓ Attack success analysis complete!")
        print("  - Each attack outcome analyzed")
        print("  - ASR calculated overall and by category")
        print("  - Results stored in results/attack_success_analysis.json")
    
    def check_rubric_compliance(self):
        """
        Additional: Check that benign responses follow rubric.
        
        Verifies:
        - Feedback follows the rubric
        - System doesn't refuse benign inputs
        - Teaching behavior is appropriate
        """
        print("\n" + "="*70)
        print("ADDITIONAL: RUBRIC COMPLIANCE CHECK")
        print("="*70)
        print("\nChecking benign responses for rubric compliance...")
        
        # Check compliance
        self.rubric_checker.analyze_benign_responses(
            eval_report_path="results/evaluation_report.json",
            output_path="results/rubric_compliance_analysis.json"
        )
        
        print("\n✓ Rubric compliance analysis complete!")
        print("  - Benign responses checked for teaching quality")
        print("  - Compliance with guidelines verified")
        print("  - Results stored in results/rubric_compliance_analysis.json")
    
    def run_complete_pipeline(self):
        """
        Run the complete research pipeline.
        
        Executes all steps in order:
        1. Baseline evaluation with no defenses
        2. Attack success analysis (RQ1)
        3. Rubric compliance checking
        """
        print("\n" + "="*80)
        print(" " * 20 + "SECURITY RESEARCH PIPELINE")
        print(" " * 15 + "Complete Baseline Evaluation & Analysis")
        print("="*80)
        
        # Step 1-2: Baseline evaluation
        self.run_baseline_evaluation()
        
        # Step 3-4: Attack success analysis
        self.analyze_attack_success()
        
        # Additional: Rubric compliance
        self.check_rubric_compliance()
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final summary of all analyses."""
        print("\n" + "="*80)
        print(" " * 30 + "PIPELINE COMPLETE")
        print("="*80)
        
        print("\n📊 Generated Reports:")
        print("  1. results/evaluation_report.json")
        print("     - Raw evaluation results for benign and attack queries")
        print("  2. results/attack_success_analysis.json")
        print("     - Attack Success Rate (ASR) and RQ1 analysis")
        print("  3. results/rubric_compliance_analysis.json")
        print("     - Rubric compliance for benign responses")
        
        print("\n📝 Next Steps for Your Thesis:")
        print("  1. Review attack_success_analysis.json for RQ1 answer")
        print("  2. Manually review attacks marked 'requires_manual_review'")
        print("  3. Run pipeline again with defenses enabled for RQ2")
        print("  4. Compare baseline vs defended ASR for RQ3")
        
        print("\n🔬 Research Questions Status:")
        print("  RQ1: ✓ Which attacks succeed? - ANSWERED (see attack_success_analysis.json)")
        print("  RQ2: ? Which defenses work? - RUN WITH DEFENSES ENABLED")
        print("  RQ3: ? What's the tradeoff? - COMPARE BASELINE VS DEFENDED")
        
        print("\n" + "="*80 + "\n")


def main():
    """Run the complete research pipeline."""
    pipeline = ResearchPipeline()
    pipeline.run_complete_pipeline()


if __name__ == "__main__":
    main()
