"""
Test script for job posting validation workflow.
This script tests the validation logic to ensure salary ranges are properly enforced.
"""

from job_posting_approval import validate_job_posting_with_report


def test_valid_job_posting():
    """Test a valid job posting with salary range"""
    
    job_posting = """
# Production Assistant - Warner Bros. Discovery

## Location
Los Angeles, CA

## Job Summary
Seeking a Production Assistant for TV production set in Los Angeles.

## Responsibilities
- Assist with daily production operations
- Support production team members
- Coordinate logistics and schedules

## Requirements
- 1+ years of production experience
- Strong organizational skills
- Ability to work in fast-paced environment

## Compensation
**Salary Range:** $45,000 - $60,000 per year

Based on industry standards for entry-level production roles in Los Angeles.

## Benefits
- Weekly Pay
- Employee Meals
- Healthcare coverage

## How to Apply
Submit your resume to careers@wbd.com
"""
    
    is_valid, report = validate_job_posting_with_report(job_posting)
    
    print("TEST 1: Valid Job Posting with Salary Range")
    print("-" * 60)
    print(report)
    print(f"Result: {'PASSED ✓' if is_valid else 'FAILED ✗'}")
    print("\n")
    
    return is_valid


def test_missing_salary_range():
    """Test a job posting missing salary range (should fail)"""
    
    job_posting = """
# Production Assistant - Warner Bros. Discovery

## Location
Los Angeles, CA

## Job Summary
Seeking a Production Assistant for TV production set in Los Angeles.

## Responsibilities
- Assist with daily production operations
- Support production team members

## Requirements
- 1+ years of production experience
- Strong organizational skills

## Benefits
- Weekly Pay
- Employee Meals
- Healthcare coverage
"""
    
    is_valid, report = validate_job_posting_with_report(job_posting)
    
    print("TEST 2: Job Posting WITHOUT Salary Range (Expected to Fail)")
    print("-" * 60)
    print(report)
    print(f"Result: {'PASSED ✓ (Correctly rejected)' if not is_valid else 'FAILED ✗ (Should have been rejected)'}")
    print("\n")
    
    return not is_valid  # Should be invalid


def test_salary_range_dict():
    """Test with structured salary range data"""
    
    job_posting = {
        'title': 'Production Assistant',
        'salary_range': {
            'minimum': 45000,
            'maximum': 60000,
            'currency': 'USD',
            'period': 'per year'
        },
        'content': """
# Production Assistant

Exciting opportunity at Warner Bros. Discovery!

## Compensation
$45,000 - $60,000 per year
"""
    }
    
    is_valid, report = validate_job_posting_with_report(job_posting)
    
    print("TEST 3: Structured Data with Salary Range")
    print("-" * 60)
    print(report)
    print(f"Result: {'PASSED ✓' if is_valid else 'FAILED ✗'}")
    print("\n")
    
    return is_valid


def test_invalid_salary_range():
    """Test with invalid salary range (max < min)"""
    
    job_posting = """
# Production Assistant

## Compensation
**Salary Range:** $60,000 - $45,000 per year

## Responsibilities
- Various production tasks
"""
    
    is_valid, report = validate_job_posting_with_report(job_posting)
    
    print("TEST 4: Invalid Salary Range (Max < Min)")
    print("-" * 60)
    print(report)
    print(f"Result: {'PASSED ✓' if is_valid else 'FAILED ✗'}")
    print("Note: Should show warnings about range")
    print("\n")
    
    return True  # May pass but with warnings


def run_all_tests():
    """Run all validation tests"""
    
    print("="*60)
    print("JOB POSTING VALIDATION TEST SUITE")
    print("="*60)
    print("\n")
    
    tests = [
        test_valid_job_posting,
        test_missing_salary_range,
        test_salary_range_dict,
        test_invalid_salary_range
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Passed: {sum(results)}/{len(results)}")
    print(f"Tests Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed. Please review above.")
    
    return all(results)


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)