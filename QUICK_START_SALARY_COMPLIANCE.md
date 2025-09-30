# Quick Start: Salary Range Compliance

## What Changed?

The job posting system now **requires** a salary range in all job postings for legal compliance.

## For Users

### Running the Job Posting Crew

The crew automatically includes salary research. No changes needed to basic usage:

```bash
cd /workspace
python3 -m job_posting.main
```

### What to Expect

The system will now:

1. ✅ Research salary ranges for your role
2. ✅ Include salary range in the draft
3. ✅ Validate salary range is present and correct
4. ✅ Reject postings without salary ranges

### Example Output

```markdown
## Compensation
**Salary Range:** $45,000 - $60,000 per year

Based on industry standards for Production Assistant roles in Los Angeles.
```

## For Developers

### Validating a Job Posting

```python
from workflows import validate_job_posting_with_report

# Your job posting (string or dict)
job_posting = """
# Job Title
...
## Compensation
$45,000 - $60,000 per year
"""

# Validate
is_valid, report = validate_job_posting_with_report(job_posting)

if is_valid:
    print("✓ Ready to publish")
else:
    print("✗ Needs revision:")
    print(report)
```

### Using the Template

```python
import yaml

# Load template
with open('templates/job_posting_template.yaml', 'r') as f:
    template = yaml.safe_load(f)

# Required salary_range structure
salary_data = {
    'minimum': 45000,
    'maximum': 60000,
    'currency': 'USD',
    'period': 'per year',
    'display_format': '$45,000 - $60,000 per year'
}
```

### Running Tests

```bash
cd /workspace/workflows
python3 test_validation.py
```

## Validation Rules

### ✅ Valid Salary Ranges

- `$45,000 - $60,000 per year`
- `$45,000 to $60,000 annually`
- `Salary Range: $45k - $60k/year`

### ❌ Invalid (Will Fail)

- Missing entirely
- "Competitive salary"
- "DOE" (Depends on Experience)
- No specific amounts

### ⚠️ Warnings

- Maximum less than minimum
- Range too narrow (< 10% difference)
- Missing recommended sections

## Production Assistant Example

For the Warner Bros. Discovery Production Assistant role:

```markdown
# Production Assistant - Warner Bros. Discovery

## Location
Los Angeles, CA

## Job Summary
Exciting opportunity to join our TV production team...

## Responsibilities
- Assist with daily production operations
- Support crew members and talent
- Coordinate logistics

## Requirements
- 1+ years production experience
- Strong organizational skills
- Team player

## Compensation
**Salary Range:** $45,000 - $60,000 per year

This range reflects industry standards for Production Assistant 
roles in Los Angeles, based on current market research.

## Benefits
- Weekly Pay
- Employee Meals
- Healthcare Coverage

## How to Apply
Submit resume to careers@wbd.com
```

## Troubleshooting

### Error: "Salary range must be provided"

**Solution:** Add a Compensation section with specific dollar amounts:

```markdown
## Compensation
**Salary Range:** $XX,XXX - $XX,XXX per year
```

### Warning: "Maximum salary should be greater than minimum"

**Solution:** Check your numbers - ensure max > min:
- ❌ $60,000 - $45,000
- ✅ $45,000 - $60,000

### Warning: "Salary range seems too narrow"

**Solution:** Provide a reasonable range (at least 10% difference):
- ❌ $50,000 - $51,000 (too narrow)
- ✅ $45,000 - $60,000 (good range)

## Benefits

✅ **Legal Compliance** - Meets transparency requirements  
✅ **Candidate Trust** - Clear expectations upfront  
✅ **Competitive Advantage** - Shows market awareness  
✅ **Quality Control** - Automated validation  

## Support

- Full documentation: `SALARY_RANGE_IMPLEMENTATION.md`
- Template: `templates/job_posting_template.yaml`
- Validation code: `workflows/job_posting_approval.py`
- Tests: `workflows/test_validation.py`

---

**Remember:** Salary range is now mandatory. The system will reject any job posting without it.