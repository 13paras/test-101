
def get_salary_range_for_band(band: str) -> str:
    band_ranges = {
        "entry": {"min": 25000, "max": 40000},
        "mid": {"min": 40000, "max": 70000},
        "senior": {"min": 70000, "max": 100000},
    }
    
    range_info = band_ranges.get(band.lower())
    if range_info:
        return f"${range_info['min']:,}–${range_info['max']:,} per year"
    return ""
