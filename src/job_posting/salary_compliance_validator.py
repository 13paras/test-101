"""
Salary Compliance Validator for Job Postings
Ensures job postings meet US jurisdictional salary transparency requirements
"""

import re
from typing import Dict, List, Tuple, Optional

class SalaryComplianceValidator:
    """Validates job postings for salary transparency compliance"""
    
    def __init__(self):
        self.salary_patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+\s*(annually|per year|yearly)',
            r'\$[\d,]+\s*-\s*\$[\d,]+\s*(per hour|hourly|/hour)',
            r'\$[\d,]+\s*-\s*\$[\d,]+',
            r'Salary Range:\s*\$[\d,]+\s*-\s*\$[\d,]+',
            r'TBD.*based on.*experience',
            r'To be determined.*experience.*qualifications'
        ]
        
        # Industry standard ranges for validation
        self.role_salary_ranges = {
            'production_assistant_la': {
                'annual_min': 44000,
                'annual_max': 54000,
                'hourly_min': 21,
                'hourly_max': 26
            }
        }
    
    def validate_posting(self, job_posting_text: str, role_type: str = None) -> Dict:
        """
        Validates a job posting for salary compliance
        
        Args:
            job_posting_text: The full text of the job posting
            role_type: Optional role type for specific validation rules
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'is_compliant': False,
            'has_salary_range': False,
            'found_salary_info': [],
            'validation_errors': [],
            'recommendations': []
        }
        
        # Check for salary range presence
        salary_matches = self._find_salary_ranges(job_posting_text)
        
        if salary_matches:
            results['has_salary_range'] = True
            results['found_salary_info'] = salary_matches
            
            # Validate range reasonableness
            if role_type == 'production_assistant_la':
                validation = self._validate_production_assistant_range(salary_matches)
                results.update(validation)
            else:
                results['is_compliant'] = True
                results['recommendations'].append('Salary range found and included')
        else:
            results['validation_errors'].append('No salary range found in job posting')
            results['recommendations'].append('Add salary range section for legal compliance')
        
        # Check for TBD with justification
        if 'TBD' in job_posting_text or 'to be determined' in job_posting_text.lower():
            if any(keyword in job_posting_text.lower() for keyword in ['experience', 'qualifications', 'based on']):
                results['has_salary_range'] = True
                results['found_salary_info'].append('TBD with justification')
                if not results['validation_errors']:
                    results['is_compliant'] = True
            else:
                results['validation_errors'].append('TBD salary range needs legal justification')
        
        return results
    
    def _find_salary_ranges(self, text: str) -> List[str]:
        """Find all salary range patterns in text"""
        found_ranges = []
        for pattern in self.salary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_ranges.extend(matches)
        
        # Also capture full salary lines
        lines = text.split('\n')
        for line in lines:
            if 'salary' in line.lower() and ('$' in line or 'tbd' in line.lower()):
                found_ranges.append(line.strip())
        
        return found_ranges
    
    def _validate_production_assistant_range(self, salary_info: List[str]) -> Dict:
        """Validate salary range for Production Assistant role"""
        validation = {
            'is_compliant': False,
            'validation_errors': [],
            'recommendations': []
        }
        
        expected_range = self.role_salary_ranges['production_assistant_la']
        
        for salary_text in salary_info:
            # Extract numbers from salary text
            numbers = re.findall(r'\$?([\d,]+)', salary_text)
            if len(numbers) >= 2:
                try:
                    low = int(numbers[0].replace(',', ''))
                    high = int(numbers[1].replace(',', ''))
                    
                    # Check if range is reasonable for Production Assistant
                    if 'hour' in salary_text.lower():
                        if (expected_range['hourly_min'] <= low <= expected_range['hourly_max'] and
                            expected_range['hourly_min'] <= high <= expected_range['hourly_max'] + 5):
                            validation['is_compliant'] = True
                            validation['recommendations'].append(f'Hourly range ${low}-${high} is within market standards')
                        else:
                            validation['validation_errors'].append(
                                f'Hourly range ${low}-${high} outside market range ${expected_range["hourly_min"]}-${expected_range["hourly_max"]}'
                            )
                    else:
                        if (expected_range['annual_min'] <= low <= expected_range['annual_max'] + 10000 and
                            expected_range['annual_min'] <= high <= expected_range['annual_max'] + 10000):
                            validation['is_compliant'] = True
                            validation['recommendations'].append(f'Annual range ${low:,}-${high:,} is within market standards')
                        else:
                            validation['validation_errors'].append(
                                f'Annual range ${low:,}-${high:,} outside market range ${expected_range["annual_min"]:,}-${expected_range["annual_max"]:,}'
                            )
                except ValueError:
                    validation['validation_errors'].append(f'Could not parse salary numbers from: {salary_text}')
        
        return validation
    
    def generate_compliance_report(self, validation_results: Dict) -> str:
        """Generate a human-readable compliance report"""
        report = "SALARY COMPLIANCE VALIDATION REPORT\n"
        report += "=" * 40 + "\n\n"
        
        if validation_results['is_compliant']:
            report += "✅ COMPLIANT: Job posting meets salary transparency requirements\n\n"
        else:
            report += "❌ NON-COMPLIANT: Job posting needs salary range corrections\n\n"
        
        if validation_results['found_salary_info']:
            report += "Found Salary Information:\n"
            for info in validation_results['found_salary_info']:
                report += f"  • {info}\n"
            report += "\n"
        
        if validation_results['validation_errors']:
            report += "Compliance Issues:\n"
            for error in validation_results['validation_errors']:
                report += f"  ❌ {error}\n"
            report += "\n"
        
        if validation_results['recommendations']:
            report += "Recommendations:\n"
            for rec in validation_results['recommendations']:
                report += f"  💡 {rec}\n"
            report += "\n"
        
        report += "Legal Requirements:\n"
        report += "  • US jurisdictional transparency laws require salary ranges in job postings\n"
        report += "  • Range must reflect market conditions\n"
        report += "  • If TBD, must include legal justification\n"
        
        return report

# Example usage and testing
if __name__ == "__main__":
    validator = SalaryComplianceValidator()
    
    # Test with compliant posting
    compliant_posting = """
    Production Assistant - Warner Bros. Discovery
    
    We are seeking a Production Assistant for our Los Angeles office.
    
    Salary Range: $44,000 - $54,000 annually (based on experience and qualifications)
    
    Benefits include health insurance and professional development opportunities.
    """
    
    # Test with non-compliant posting
    non_compliant_posting = """
    Production Assistant - Warner Bros. Discovery
    
    We are seeking a Production Assistant for our Los Angeles office.
    
    Competitive salary and great benefits!
    """
    
    print("Testing Compliant Posting:")
    results = validator.validate_posting(compliant_posting, 'production_assistant_la')
    print(validator.generate_compliance_report(results))
    
    print("\n" + "="*50 + "\n")
    
    print("Testing Non-Compliant Posting:")
    results = validator.validate_posting(non_compliant_posting, 'production_assistant_la')
    print(validator.generate_compliance_report(results))