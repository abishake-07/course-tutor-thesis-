"""
Comprehensive logging system for the course tutor
Tracks all interactions, attacks, defenses, and feedback
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class TutorLogger:
    """
    Comprehensive logging system for security research and system monitoring
    """
    
    def __init__(self, log_dir: str = "logs", session_id: str = None):
        """
        Initialize the logging system
        
        Args:
            log_dir: Directory to store log files
            session_id: Unique session identifier
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = session_id or self._generate_session_id()
        
        # Create separate log files
        self.interaction_log_path = self.log_dir / f"{self.session_id}_interactions.jsonl"
        self.attack_log_path = self.log_dir / f"{self.session_id}_attacks.jsonl"
        self.defense_log_path = self.log_dir / f"{self.session_id}_defenses.jsonl"
        self.feedback_log_path = self.log_dir / f"{self.session_id}_feedback.jsonl"
        self.system_log_path = self.log_dir / f"{self.session_id}_system.log"
        
        # Setup standard Python logger for system events
        self._setup_system_logger()
        
        # Statistics tracking
        self.stats = {
            "total_interactions": 0,
            "blocked_interactions": 0,
            "attacks_detected": 0,
            "defenses_triggered": 0,
            "feedback_generated": 0,
            "errors": 0
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def _setup_system_logger(self):
        """Setup standard Python logging"""
        self.system_logger = logging.getLogger(f"CoursTutor_{self.session_id}")
        self.system_logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.system_log_path)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.system_logger.addHandler(fh)
        self.system_logger.addHandler(ch)
    
    def _write_jsonl(self, filepath: Path, data: Dict):
        """Write a JSON line to a JSONL file"""
        with open(filepath, 'a', encoding='utf-8') as f:
            json.dump(data, f)
            f.write('\n')
    
    def log_interaction(self, 
                       user_message: str,
                       assistant_response: str,
                       blocked: bool = False,
                       defense_log: Optional[Dict] = None,
                       metadata: Optional[Dict] = None):
        """
        Log a complete interaction between user and tutor
        
        Args:
            user_message: The user's input
            assistant_response: The tutor's response
            blocked: Whether the interaction was blocked
            defense_log: Defense mechanism activity
            metadata: Additional metadata
        """
        self.stats["total_interactions"] += 1
        if blocked:
            self.stats["blocked_interactions"] += 1
        
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "interaction_id": self.stats["total_interactions"],
            "user_message": user_message,
            "assistant_response": assistant_response,
            "blocked": blocked,
            "defense_log": defense_log or {},
            "metadata": metadata or {}
        }
        
        self._write_jsonl(self.interaction_log_path, interaction_data)
        self.system_logger.info(f"Interaction {self.stats['total_interactions']} logged (blocked={blocked})")
    
    def log_attack(self,
                  attack_id: str,
                  attack_type: str,
                  attack_payload: str,
                  detected: bool,
                  blocked: bool,
                  detection_method: Optional[str] = None,
                  success_criteria_met: Optional[Dict] = None,
                  metadata: Optional[Dict] = None):
        """
        Log an attack attempt
        
        Args:
            attack_id: Unique attack identifier
            attack_type: Category of attack
            attack_payload: The attack content
            detected: Whether attack was detected
            blocked: Whether attack was blocked
            detection_method: How the attack was detected
            success_criteria_met: Which success criteria were achieved
            metadata: Additional attack metadata
        """
        self.stats["attacks_detected"] += 1
        
        attack_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "attack_id": attack_id,
            "attack_type": attack_type,
            "attack_payload": attack_payload,
            "detected": detected,
            "blocked": blocked,
            "detection_method": detection_method,
            "success_criteria_met": success_criteria_met or {},
            "metadata": metadata or {}
        }
        
        self._write_jsonl(self.attack_log_path, attack_data)
        self.system_logger.warning(f"Attack {attack_id} logged (detected={detected}, blocked={blocked})")
    
    def log_defense_activation(self,
                               defense_type: str,
                               triggered: bool,
                               action_taken: str,
                               input_content: str,
                               threat_indicators: Optional[List] = None,
                               metadata: Optional[Dict] = None):
        """
        Log defense mechanism activation
        
        Args:
            defense_type: Type of defense (delimiter, sanitization, detection)
            triggered: Whether defense was triggered
            action_taken: What action was taken
            input_content: The content that triggered the defense
            threat_indicators: Specific threats detected
            metadata: Additional defense metadata
        """
        self.stats["defenses_triggered"] += 1
        
        defense_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "defense_type": defense_type,
            "triggered": triggered,
            "action_taken": action_taken,
            "input_content": input_content[:500],  # Truncate for storage
            "threat_indicators": threat_indicators or [],
            "metadata": metadata or {}
        }
        
        self._write_jsonl(self.defense_log_path, defense_data)
        self.system_logger.info(f"Defense '{defense_type}' logged (triggered={triggered})")
    
    def log_feedback(self,
                    feedback_type: str,
                    submission_content: str,
                    feedback_generated: str,
                    rubric_scores: Optional[Dict] = None,
                    total_score: Optional[Dict] = None,
                    metadata: Optional[Dict] = None):
        """
        Log feedback generation
        
        Args:
            feedback_type: Type of feedback (grading, code_review, question_answer)
            submission_content: What was submitted
            feedback_generated: The feedback provided
            rubric_scores: Scores per rubric criterion
            total_score: Overall score calculation
            metadata: Additional feedback metadata
        """
        self.stats["feedback_generated"] += 1
        
        feedback_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "feedback_id": self.stats["feedback_generated"],
            "feedback_type": feedback_type,
            "submission_content": submission_content[:1000],  # Truncate
            "feedback_generated": feedback_generated,
            "rubric_scores": rubric_scores or {},
            "total_score": total_score or {},
            "metadata": metadata or {}
        }
        
        self._write_jsonl(self.feedback_log_path, feedback_data)
        self.system_logger.info(f"Feedback {self.stats['feedback_generated']} logged (type={feedback_type})")
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict] = None):
        """
        Log an error
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        self.stats["errors"] += 1
        
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        # Log to system logger
        self.system_logger.error(f"Error: {error_type} - {error_message}")
        
        # Also log to JSONL for analysis
        error_log_path = self.log_dir / f"{self.session_id}_errors.jsonl"
        self._write_jsonl(error_log_path, error_data)
    
    def get_statistics(self) -> Dict:
        """Get current session statistics"""
        return {
            "session_id": self.session_id,
            "statistics": self.stats.copy(),
            "log_files": {
                "interactions": str(self.interaction_log_path),
                "attacks": str(self.attack_log_path),
                "defenses": str(self.defense_log_path),
                "feedback": str(self.feedback_log_path),
                "system": str(self.system_log_path)
            }
        }
    
    def export_session_summary(self, output_path: Optional[str] = None) -> str:
        """
        Export a comprehensive session summary
        
        Args:
            output_path: Path to save summary (default: logs/session_id_summary.json)
            
        Returns:
            Path to summary file
        """
        if output_path is None:
            output_path = self.log_dir / f"{self.session_id}_summary.json"
        
        summary = {
            "session_id": self.session_id,
            "session_start": self.session_id.split('_', 1)[1],
            "statistics": self.stats,
            "log_files": {
                "interactions": str(self.interaction_log_path),
                "attacks": str(self.attack_log_path),
                "defenses": str(self.defense_log_path),
                "feedback": str(self.feedback_log_path),
                "system": str(self.system_log_path)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        self.system_logger.info(f"Session summary exported to {output_path}")
        return str(output_path)


def read_jsonl_logs(log_path: str) -> List[Dict]:
    """
    Read and parse a JSONL log file
    
    Args:
        log_path: Path to JSONL log file
        
    Returns:
        List of log entries
    """
    logs = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
    return logs


def analyze_attack_logs(attack_log_path: str) -> Dict:
    """
    Analyze attack log file and generate statistics
    
    Args:
        attack_log_path: Path to attack log file
        
    Returns:
        Dictionary with attack statistics
    """
    attacks = read_jsonl_logs(attack_log_path)
    
    if not attacks:
        return {"total_attacks": 0}
    
    total_attacks = len(attacks)
    detected_attacks = sum(1 for a in attacks if a.get('detected', False))
    blocked_attacks = sum(1 for a in attacks if a.get('blocked', False))
    
    # Count by type
    attack_types = {}
    for attack in attacks:
        att_type = attack.get('attack_type', 'unknown')
        attack_types[att_type] = attack_types.get(att_type, 0) + 1
    
    # Detection methods
    detection_methods = {}
    for attack in attacks:
        if attack.get('detected'):
            method = attack.get('detection_method', 'unknown')
            detection_methods[method] = detection_methods.get(method, 0) + 1
    
    return {
        "total_attacks": total_attacks,
        "detected_attacks": detected_attacks,
        "blocked_attacks": blocked_attacks,
        "detection_rate": (detected_attacks / total_attacks * 100) if total_attacks > 0 else 0,
        "block_rate": (blocked_attacks / total_attacks * 100) if total_attacks > 0 else 0,
        "attack_types": attack_types,
        "detection_methods": detection_methods
    }
