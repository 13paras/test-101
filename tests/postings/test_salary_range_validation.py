import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from validation.posting_validator import validate_salary_range_in_posting, ValidationError

def test_salary_range_present_finalization_pass():
    posting = {
        'role': 'Production Assistant',
        'salary_range': {
            'min': '50000',
            'max': '70000',
            'currency': 'USD',
            'period': 'per year'
        }
    }
    assert validate_salary_range_in_posting(posting, is_final=True) is True

def test_salary_range_missing_finalization_fails():
    posting = {
        'role': 'Production Assistant',
        # salary_range missing
    }
    with pytest.raises(ValidationError, match="Salary Range is required for final postings"):
        validate_salary_range_in_posting(posting, is_final=True)

def test_salary_range_placeholder_allowed_in_draft():
    posting = {
        'role': 'Production Assistant',
        'salary_range': {
            'min': '$X',
            'max': '$Y',
            'currency': 'USD',
            'period': 'per year'
        }
    }
    # Should not raise exception
    assert validate_salary_range_in_posting(posting, is_final=False) is True

def test_salary_range_placeholder_fails_in_final():
    posting = {
        'role': 'Production Assistant',
        'salary_range': {
            'min': '$X',
            'max': '$Y',
            'currency': 'USD',
            'period': 'per year'
        }
    }
    with pytest.raises(ValidationError, match="actual min and max values instead of placeholders"):
        validate_salary_range_in_posting(posting, is_final=True)
