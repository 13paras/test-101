import logging

class ValidationError(Exception):
    pass

def is_valid_range(range_dict):
    """
    Verifies min and max exist and are numeric or properly formatted strings like "$X".
    """
    if not range_dict or not isinstance(range_dict, dict):
        return False
    
    min_val = range_dict.get('min')
    max_val = range_dict.get('max')
    
    if min_val is None or max_val is None:
        return False
        
    def is_numeric_or_placeholder(val):
        if isinstance(val, (int, float)):
            return True
        if isinstance(val, str):
            if val in ["$X", "$Y"]:
                return True
            # Try to strip $ and check if numeric
            try:
                clean_val = val.replace('$', '').replace(',', '').strip()
                float(clean_val)
                return True
            except ValueError:
                return False
        return False

    return is_numeric_or_placeholder(min_val) and is_numeric_or_placeholder(max_val)

def validate_salary_range_in_posting(posting_dict, is_final=False):
    """
    Validates the presence and format of salary range in a job posting.
    """
    salary_range = posting_dict.get('salary_range')
    
    if is_final:
        if not salary_range or not is_valid_range(salary_range):
            raise ValidationError("Salary Range is required for final postings. Please provide min, max, currency, and period.")
        
        # In final, we don't want placeholders $X or $Y
        if salary_range.get('min') == "$X" or salary_range.get('max') == "$Y":
             raise ValidationError("Salary Range is required for final postings. Please provide actual min and max values instead of placeholders.")
    else:
        if not salary_range:
            logging.warning("Salary Range block is missing in the draft posting.")
        elif not is_valid_range(salary_range):
             logging.warning("Salary Range block exists but is not valid.")
        else:
            if salary_range.get('min') == "$X" or salary_range.get('max') == "$Y":
                logging.info("Salary Range contains placeholders (allowed in draft).")
                
    return True
