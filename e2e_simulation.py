import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from writers.job_description_writer import generate_production_assistant_posting
from validation.posting_validator import validate_salary_range_in_posting, ValidationError

def run_e2e_simulation():
    print("--- E2E Simulation: Production Assistant Posting Generation ---")
    
    # Case 1: Known Salary Range
    print("\n[Case 1] Known Salary Range")
    context_known = {
        'description': 'Help with TV production in LA.',
        'benefits': 'Weekly Pay, Employee Meals',
        'salary_range': {
            'min': '40000',
            'max': '60000',
            'currency': 'USD',
            'period': 'per year'
        }
    }
    posting_known = generate_production_assistant_posting(context_known)
    print("Generated Posting (Excerpt):")
    for line in posting_known.split("\n"):
        if "## Compensation" in line or "Salary Range:" in line:
            print(line)
    
    try:
        validate_salary_range_in_posting(context_known, is_final=True)
        print("Validation (Final): PASS")
    except ValidationError as e:
        print(f"Validation (Final): FAIL - {e}")

    # Case 2: Unknown Salary (Placeholder)
    print("\n[Case 2] Unknown Salary (Placeholder)")
    context_unknown = {
        'description': 'Help with TV production in LA.',
        'benefits': 'Weekly Pay, Employee Meals'
    }
    posting_unknown = generate_production_assistant_posting(context_unknown)
    print("Generated Posting (Excerpt):")
    for line in posting_unknown.split("\n"):
        if "## Compensation" in line or "Salary Range:" in line:
            print(line)
    
    try:
        validate_salary_range_in_posting(context_unknown, is_final=False)
        print("Validation (Draft): PASS")
    except ValidationError as e:
        print(f"Validation (Draft): FAIL - {e}")
        
    try:
        # We need to simulate the dictionary that would be passed to validator
        # The writer returns a string, but validator expects a dict.
        # In a real pipeline, the context/dict would be validated.
        validate_salary_range_in_posting(context_unknown, is_final=True)
        print("Validation (Final): PASS")
    except ValidationError as e:
        print(f"Validation (Final): FAIL (Expected) - {e}")

if __name__ == "__main__":
    run_e2e_simulation()
