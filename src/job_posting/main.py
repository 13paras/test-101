import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import sys

from job_posting.crew import JobPostingCrew
import neatlogs

load_dotenv()

neatlogs.init(api_key=os.getenv('NEATLOGS_API_KEY'), tags=['crewai'])

_CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
}


def _format_salary_range(salary_data: Optional[Dict[str, Any]]) -> Optional[str]:
    """Return a human readable salary range or None when data is incomplete."""
    if not salary_data:
        return None

    min_salary = salary_data.get('min')
    max_salary = salary_data.get('max')
    if min_salary is None or max_salary is None:
        return None

    currency_code = str(salary_data.get('currency', 'USD')).upper()
    period = salary_data.get('period', 'per year')
    currency_symbol = salary_data.get(
        'currency_symbol', _CURRENCY_SYMBOLS.get(currency_code, '')
    )

    if currency_symbol:
        formatted_min = f"{currency_symbol}{min_salary:,.0f}"
        formatted_max = f"{currency_symbol}{max_salary:,.0f}"
    else:
        formatted_min = f"{min_salary:,.0f} {currency_code}"
        formatted_max = f"{max_salary:,.0f} {currency_code}"

    return f"{formatted_min} - {formatted_max} {period}"


def _default_inputs() -> Dict[str, Any]:
    salary_data = {
        'min': 72000,
        'max': 86000,
        'currency': 'USD',
        'period': 'per year',
    }
    salary_range = _format_salary_range(salary_data)

    inputs: Dict[str, Any] = {
        'company_domain': 'careers.wbd.com',
        'company_description': "Warner Bros. Discovery is a premier global media and entertainment company, offering audiences the world’s most differentiated and complete portfolio of content, brands and franchises across television, film, sports, news, streaming and gaming. We're home to the world’s best storytellers, creating world-class products for consumers",
        'hiring_needs': 'Production Assistant, for a TV production set in Los Angeles in June 2025',
        'specific_benefits': 'Weekly Pay, Employee Meals, healthcare',
        'salary_range': salary_range or '',
        'salaryRange': salary_range or '',
        'has_salary_data': 'true' if salary_range else 'false',
    }
    return inputs


def run():
    """Kick off the crew with the default sample inputs."""
    JobPostingCrew().crew().kickoff(inputs=_default_inputs())


def train():
    """
    Train the crew for a given number of iterations.
    """
    try:
        JobPostingCrew().crew().train(
            n_iterations=int(sys.argv[1]), inputs=_default_inputs())

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
