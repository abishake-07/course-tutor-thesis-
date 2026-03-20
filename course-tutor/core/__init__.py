"""
Core package for Course Tutor system
"""

from .pipeline import CourseTutor
from .defenses import DefenseManager, extract_pdf_text
from .logging_system import TutorLogger
from .utils import get_system_prompt, ASSIGNMENT_RUBRIC, calculate_total_score, format_rubric_for_prompt

__all__ = [
    'CourseTutor',
    'DefenseManager',
    'extract_pdf_text',
    'TutorLogger',
    'get_system_prompt',
    'ASSIGNMENT_RUBRIC',
    'calculate_total_score',
    'format_rubric_for_prompt',
]
