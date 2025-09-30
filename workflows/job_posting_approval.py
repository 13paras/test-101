"""
Job Posting Approval Workflow
This module provides validation logic to ensure job postings comply with legal requirements,
specifically including mandatory salary range information.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error in a job posting"""
    field: str
    message: str
    severity: str  # 'error' or 'warning'


class JobPostingValidator:
    """Validates job postings for compliance and completeness"""
    
    SALARY_RANGE_PATTERNS = [
        r'\$[\d,]+\s*-\s*\$[\d,]+',  # $45,000 - $60,000
        r'\$[\d,]+\s+to\s+\$[\d,]+',  # $45,000 to $60,000
        r'[\d,]+\s*-\s*[\d,]+',       # 45,000 - 60,000
    ]
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate_job_posting(self, job_posting: Dict[str, any]) -> bool:
        """
        Validate a job posting for compliance and completeness.
        
        Args:
            job_posting: Dictionary containing job posting data or markdown string
            
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            ValueError: If salary range is missing (critical compliance requirement)
        """
        self.errors = []
        self.warnings = []
        
        # Convert to string if it's a markdown string
        if isinstance(job_posting, str):
            posting_text = job_posting
            job_posting = {'content': posting_text}
        else:
            posting_text = job_posting.get('content', str(job_posting))
        
        # Critical validation: Check for salary range
        if not self._validate_salary_range(posting_text, job_posting):
            error = ValidationError(
                field='salary_range',
                message='Salary range must be provided for legal compliance and transparency.',
                severity='error'
            )
            self.errors.append(error)
            raise ValueError("Salary range must be provided.")
        
        # Additional validations
        self._validate_required_sections(posting_text)
        self._validate_salary_range_format(posting_text)
        
        # Return True only if no errors
        return len(self.errors) == 0
    
    def _validate_salary_range(self, posting_text: str, job_posting: Dict) -> bool:
        """Check if salary range is present in the job posting"""
        
        # Check in structured data first
        if isinstance(job_posting, dict) and 'salary_range' in job_posting:
            salary_range = job_posting['salary_range']
            if salary_range and str(salary_range).strip():
                return True
        
        # Check in text content
        posting_lower = posting_text.lower()
        
        # Look for salary/compensation section headers
        salary_keywords = [
            'salary range', 'compensation', 'pay range', 
            'salary:', 'compensation:', 'pay:'
        ]
        
        has_salary_section = any(keyword in posting_lower for keyword in salary_keywords)
        
        if not has_salary_section:
            return False
        
        # Verify it contains actual dollar amounts
        has_amount = any(re.search(pattern, posting_text) for pattern in self.SALARY_RANGE_PATTERNS)
        
        return has_amount
    
    def _validate_salary_range_format(self, posting_text: str) -> None:
        """Validate that salary range is in proper format"""
        
        # Find salary range in text
        salary_match = None
        for pattern in self.SALARY_RANGE_PATTERNS:
            salary_match = re.search(pattern, posting_text)
            if salary_match:
                break
        
        if salary_match:
            salary_text = salary_match.group(0)
            
            # Extract numbers
            numbers = re.findall(r'[\d,]+', salary_text.replace(',', ''))
            
            if len(numbers) >= 2:
                try:
                    min_salary = int(numbers[0])
                    max_salary = int(numbers[1])
                    
                    if min_salary >= max_salary:
                        self.warnings.append(ValidationError(
                            field='salary_range',
                            message=f'Maximum salary ({max_salary}) should be greater than minimum ({min_salary})',
                            severity='warning'
                        ))
                    
                    # Check for reasonable range (at least 10% difference)
                    if max_salary < min_salary * 1.1:
                        self.warnings.append(ValidationError(
                            field='salary_range',
                            message='Salary range seems too narrow. Consider a wider range for flexibility.',
                            severity='warning'
                        ))
                except ValueError:
                    pass
    
    def _validate_required_sections(self, posting_text: str) -> None:
        """Validate that required sections are present"""
        
        required_sections = {
            'responsibilities': ['responsibilities', 'duties', 'what you\'ll do'],
            'requirements': ['requirements', 'qualifications', 'what we\'re looking for'],
            'benefits': ['benefits', 'what we offer', 'perks'],
        }
        
        posting_lower = posting_text.lower()
        
        for section_name, keywords in required_sections.items():
            if not any(keyword in posting_lower for keyword in keywords):
                self.warnings.append(ValidationError(
                    field=section_name,
                    message=f'Consider adding a {section_name.title()} section',
                    severity='warning'
                ))
    
    def get_validation_report(self) -> str:
        """Generate a human-readable validation report"""
        
        report = []
        
        if self.errors:
            report.append("ERRORS (Must be fixed):")
            for error in self.errors:
                report.append(f"  - [{error.field}] {error.message}")
        
        if self.warnings:
            report.append("\nWARNINGS (Recommendations):")
            for warning in self.warnings:
                report.append(f"  - [{warning.field}] {warning.message}")
        
        if not self.errors and not self.warnings:
            report.append("✓ All validations passed!")
        
        return "\n".join(report)


def validate_job_posting(job_posting: Dict[str, any]) -> bool:
    """
    Main validation function for job postings.
    
    Args:
        job_posting: Dictionary containing job posting data or markdown string
        
    Returns:
        bool: True if validation passes, False otherwise
        
    Raises:
        ValueError: If salary range is missing (critical compliance requirement)
    """
    validator = JobPostingValidator()
    return validator.validate_job_posting(job_posting)


def validate_job_posting_with_report(job_posting: Dict[str, any]) -> tuple[bool, str]:
    """
    Validate job posting and return detailed report.
    
    Args:
        job_posting: Dictionary containing job posting data or markdown string
        
    Returns:
        tuple: (is_valid, validation_report)
    """
    validator = JobPostingValidator()
    try:
        is_valid = validator.validate_job_posting(job_posting)
        report = validator.get_validation_report()
        return is_valid, report
    except ValueError as e:
        report = validator.get_validation_report()
        return False, report