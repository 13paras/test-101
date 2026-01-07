import os

def generate_production_assistant_posting(posting_context):
    """
    Generates a Production Assistant job posting, ensuring a salary range is present.
    """
    if 'salary_range' in posting_context and posting_context['salary_range']:
        min_val = posting_context['salary_range'].get('min', '$X')
        max_val = posting_context['salary_range'].get('max', '$Y')
        currency = posting_context['salary_range'].get('currency', 'USD')
        period = posting_context['salary_range'].get('period', 'per year')
        salary_block = f"Salary Range: {min_val}–{max_val} {currency} {period}"
    else:
        salary_block = "Salary Range: $X–$Y per year (placeholder; update with exact figures)"

    posting = f"""
# Job Posting: Production Assistant

## Role Description
{posting_context.get('description', 'Join our team as a Production Assistant.')}

## Compensation
{salary_block}

## Benefits
{posting_context.get('benefits', 'Weekly Pay, Employee Meals, healthcare')}
"""
    return posting.strip()
