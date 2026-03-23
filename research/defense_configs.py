"""
Defense Configuration Manager
Defines and manages multiple defense configurations for comprehensive testing.
"""

from typing import Dict, List


class DefenseConfig:
    """Represents a defense configuration."""
    
    def __init__(self, name: str, description: str, config: Dict):
        self.name = name
        self.description = description
        self.config = config
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML config."""
        return self.config


# Defense D: Multiple configurations for testing
DEFENSE_CONFIGURATIONS = {
    "baseline": DefenseConfig(
        name="Baseline (No Defenses)",
        description="No defenses enabled - measures natural LLM resistance",
        config={
            "enabled": False,
            "delimiter_isolation": False,
            "pdf_sanitization": False,
            "prompt_injection_detection": False,
            "trigger_phrase_detection": False,
            "text_normalization": False
        }
    ),
    
    "delimiter_only": DefenseConfig(
        name="Delimiter Isolation Only",
        description="Only [SYSTEM]/[STUDENT] delimiter-based isolation",
        config={
            "enabled": True,
            "delimiter_isolation": True,
            "pdf_sanitization": False,
            "prompt_injection_detection": False,
            "trigger_phrase_detection": False,
            "text_normalization": False
        }
    ),
    
    "pdf_sanitization_only": DefenseConfig(
        name="PDF Sanitization Only",
        description="Only PDF content sanitization (for PDF inputs)",
        config={
            "enabled": True,
            "delimiter_isolation": False,
            "pdf_sanitization": True,
            "prompt_injection_detection": False,
            "trigger_phrase_detection": False,
            "text_normalization": False
        }
    ),
    
    "delimiter_pdf": DefenseConfig(
        name="Delimiter + PDF Sanitization",
        description="Combination of delimiter isolation and PDF sanitization",
        config={
            "enabled": True,
            "delimiter_isolation": True,
            "pdf_sanitization": True,
            "prompt_injection_detection": False,
            "trigger_phrase_detection": False,
            "text_normalization": False
        }
    ),
    
    "regex_detection_only": DefenseConfig(
        name="Regex Injection Detection Only",
        description="Pattern-based prompt injection detection",
        config={
            "enabled": True,
            "delimiter_isolation": False,
            "pdf_sanitization": False,
            "prompt_injection_detection": True,
            "trigger_phrase_detection": False,
            "text_normalization": False
        }
    ),
    
    "trigger_detection_only": DefenseConfig(
        name="Trigger Phrase Detection Only",
        description="Simple trigger phrase detection (Defense C.1)",
        config={
            "enabled": True,
            "delimiter_isolation": False,
            "pdf_sanitization": False,
            "prompt_injection_detection": False,
            "trigger_phrase_detection": True,
            "text_normalization": False
        }
    ),
    
    "normalization_only": DefenseConfig(
        name="Text Normalization Only",
        description="Light text normalization (Defense C.2)",
        config={
            "enabled": True,
            "delimiter_isolation": False,
            "pdf_sanitization": False,
            "prompt_injection_detection": False,
            "trigger_phrase_detection": False,
            "text_normalization": True
        }
    ),

    "semantic_detection_only": DefenseConfig(
        name="Semantic Risk Detection Only",
        description="Weighted multi-signal semantic risk detection (Defense C.3)",
        config={
            "enabled": True,
            "delimiter_isolation": False,
            "pdf_sanitization": False,
            "prompt_injection_detection": False,
            "trigger_phrase_detection": False,
            "text_normalization": False,
            "semantic_risk_detection": True,
            "semantic_block_threshold": 0.70,
            "semantic_review_threshold": 0.45
        }
    ),
    
    "all_detection": DefenseConfig(
        name="All Detection Methods",
        description="Regex + trigger phrase detection combined",
        config={
            "enabled": True,
            "delimiter_isolation": False,
            "pdf_sanitization": False,
            "prompt_injection_detection": True,
            "trigger_phrase_detection": True,
            "text_normalization": False
        }
    ),
    
    "full_defense": DefenseConfig(
        name="Full Defense Stack",
        description="All defenses enabled",
        config={
            "enabled": True,
            "delimiter_isolation": True,
            "pdf_sanitization": True,
            "prompt_injection_detection": True,
            "trigger_phrase_detection": True,
            "text_normalization": True,
            "semantic_risk_detection": True,
            "semantic_block_threshold": 0.70,
            "semantic_review_threshold": 0.45
        }
    ),
    
    "recommended": DefenseConfig(
        name="Recommended Configuration",
        description="Balanced: delimiter + regex + semantic detection + normalization",
        config={
            "enabled": True,
            "delimiter_isolation": True,
            "pdf_sanitization": True,
            "prompt_injection_detection": True,
            "trigger_phrase_detection": False,  # Redundant with regex
            "text_normalization": True,
            "semantic_risk_detection": True,
            "semantic_block_threshold": 0.70,
            "semantic_review_threshold": 0.45
        }
    )
}


def get_config_names() -> List[str]:
    """Get list of all configuration names."""
    return list(DEFENSE_CONFIGURATIONS.keys())


def get_config(name: str) -> DefenseConfig:
    """Get a specific defense configuration."""
    if name not in DEFENSE_CONFIGURATIONS:
        raise ValueError(f"Unknown configuration: {name}. Available: {get_config_names()}")
    return DEFENSE_CONFIGURATIONS[name]


def get_all_configs() -> Dict[str, DefenseConfig]:
    """Get all defense configurations."""
    return DEFENSE_CONFIGURATIONS
