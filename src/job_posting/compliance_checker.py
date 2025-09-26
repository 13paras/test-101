#!/usr/bin/env python3
"""
Compliance checker for job postings to ensure they meet legal requirements.
Specifically checks for California SB 1162 pay transparency compliance.
"""

import re
from pathlib import Path

def check_salary_compliance(job_posting_content: str) -> dict:
    """
    Check if a job posting complies with California pay transparency laws.
    
    Args:
        job_posting_content: The full text of the job posting
        
    Returns:
        dict: Compliance check results
    """
    results = {
        "compliant": True,
        "issues": [],
        "warnings": [],
        "salary_found": False,
        "salary_range": None,
        "legal_disclaimer": False
    }
    
    # Check for salary range patterns
    salary_patterns = [
        r'\$[\d,]+\s*[-–]\s*\$[\d,]+',  # $35,000 - $45,000
        r'\$[\d,]+\s*to\s*\$[\d,]+',    # $35,000 to $45,000
        r'salary.*range.*\$[\d,]+',      # salary range: $35,000
        r'compensation.*\$[\d,]+',       # compensation: $35,000
        r'annual.*\$[\d,]+',             # annual: $35,000
    ]
    
    content_lower = job_posting_content.lower()
    
    # Check for salary information
    for pattern in salary_patterns:
        if re.search(pattern, job_posting_content, re.IGNORECASE):
            results["salary_found"] = True
            match = re.search(pattern, job_posting_content, re.IGNORECASE)
            results["salary_range"] = match.group(0)
            break
    
    if not results["salary_found"]:
        results["compliant"] = False
        results["issues"].append("No salary range found in job posting")
    
    # Check for legal compliance language
    compliance_keywords = [
        "pay transparency",
        "california",
        "sb 1162",
        "good faith estimate",
        "compensation range complies"
    ]
    
    if any(keyword in content_lower for keyword in compliance_keywords):
        results["legal_disclaimer"] = True
    else:
        results["warnings"].append("Consider adding legal compliance disclaimer")
    
    # Check for location (important for determining which laws apply)
    if "los angeles" in content_lower or "california" in content_lower or "ca" in job_posting_content:
        if not results["salary_found"]:
            results["issues"].append("California position requires salary range disclosure")
    
    # Check for benefits information
    if "benefits" not in content_lower:
        results["warnings"].append("Consider including benefits information")
    
    return results

def main():
    """Main function to check compliance of job postings."""
    
    # Check our compliant job posting
    compliant_posting_path = Path("compliant_production_assistant_posting.md")
    
    if compliant_posting_path.exists():
        with open(compliant_posting_path, 'r') as f:
            content = f.read()
        
        print("=== Compliance Check for Production Assistant Job Posting ===\n")
        results = check_salary_compliance(content)
        
        print(f"Overall Compliance: {'✅ COMPLIANT' if results['compliant'] else '❌ NON-COMPLIANT'}")
        print(f"Salary Range Found: {'✅ YES' if results['salary_found'] else '❌ NO'}")
        
        if results['salary_range']:
            print(f"Detected Salary: {results['salary_range']}")
        
        print(f"Legal Disclaimer: {'✅ YES' if results['legal_disclaimer'] else '⚠️ MISSING'}")
        
        if results['issues']:
            print("\n🚨 ISSUES (Must Fix):")
            for issue in results['issues']:
                print(f"  - {issue}")
        
        if results['warnings']:
            print("\n⚠️ WARNINGS (Recommended):")
            for warning in results['warnings']:
                print(f"  - {warning}")
        
        if results['compliant'] and not results['issues']:
            print("\n✅ This job posting meets California pay transparency requirements!")
            print("✅ Ready for publication in Los Angeles, CA")
        
    else:
        print("❌ Compliant job posting file not found")

if __name__ == "__main__":
    main()