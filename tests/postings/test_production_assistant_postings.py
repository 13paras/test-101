import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from writers.job_description_writer import generate_production_assistant_posting

def test_writer_with_salary_range():
    context = {
        'description': 'Work on a major TV set.',
        'benefits': 'Health insurance, free lunch.',
        'salary_range': {
            'min': '45000',
            'max': '55000',
            'currency': 'USD',
            'period': 'per year'
        }
    }
    output = generate_production_assistant_posting(context)
    assert "Salary Range: 45000–55000 USD per year" in output
    assert "## Compensation" in output

def test_writer_without_salary_range_injects_placeholder():
    context = {
        'description': 'Work on a major TV set.',
        'benefits': 'Health insurance, free lunch.'
        # No salary_range
    }
    output = generate_production_assistant_posting(context)
    assert "Salary Range: $X–$Y per year (placeholder; update with exact figures)" in output
    assert "## Compensation" in output
