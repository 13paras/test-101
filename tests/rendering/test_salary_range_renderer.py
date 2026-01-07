import pytest
import math
from job_posting.crew import SalaryInfo

def test_salary_info_both_present():
    info = SalaryInfo(salary_min=50000, salary_max=75000)
    assert info.get_formatted_range() == "50000 - 75000"

def test_salary_info_only_min():
    info = SalaryInfo(salary_min=50000, salary_max=None)
    assert info.get_formatted_range() is None

def test_salary_info_only_max():
    info = SalaryInfo(salary_min=None, salary_max=75000)
    assert info.get_formatted_range() is None

def test_salary_info_none():
    info = SalaryInfo(salary_min=None, salary_max=None)
    assert info.get_formatted_range() is None

def test_salary_info_nan():
    info = SalaryInfo(salary_min=float('nan'), salary_max=75000)
    assert info.salary_min is None
    assert info.get_formatted_range() is None

def test_salary_info_non_numeric():
    # Pydantic might raise an error if typed as float, but our validator handles 'before'
    info = SalaryInfo(salary_min="invalid", salary_max=75000)
    assert info.salary_min is None
    assert info.get_formatted_range() is None
