"""
Validation Callback for Job Posting Crew
This module integrates the job posting approval workflow with CrewAI tasks.
"""

import sys
import os

# Add workflows directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from workflows.job_posting_approval import validate_job_posting_with_report


def validate_final_job_posting(task_output) -> str:
    """
    Callback to validate job posting after review task.
    
    Args:
        task_output: The output from the review task
        
    Returns:
        str: Validation report
    """
    
    # Extract the job posting content
    if hasattr(task_output, 'raw'):
        job_posting_content = task_output.raw
    else:
        job_posting_content = str(task_output)
    
    # Validate the job posting
    is_valid, report = validate_job_posting_with_report(job_posting_content)
    
    # Print validation results
    print("\n" + "="*60)
    print("JOB POSTING VALIDATION REPORT")
    print("="*60)
    print(report)
    print("="*60)
    
    if not is_valid:
        print("\n⚠️  WARNING: Job posting failed validation!")
        print("Please review and address the issues above before publishing.")
    else:
        print("\n✓ Job posting passed all validation checks!")
        print("Ready for publishing.")
    
    print("="*60 + "\n")
    
    return report


def check_salary_range_in_output(output: str) -> bool:
    """
    Quick check to verify salary range is present in output.
    
    Args:
        output: The job posting text
        
    Returns:
        bool: True if salary range is present
    """
    output_lower = output.lower()
    
    salary_indicators = [
        'salary range',
        'compensation',
        'pay range',
        '$'
    ]
    
    return any(indicator in output_lower for indicator in salary_indicators)