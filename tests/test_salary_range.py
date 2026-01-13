import unittest
from src.job_posting.compensation import get_salary_range_for_band
from src.job_posting.models import JobPosting
from pydantic import ValidationError

class TestSalaryRange(unittest.TestCase):
    def test_get_salary_range_for_band(self):
        self.assertEqual(get_salary_range_for_band("entry"), "$25,000–$40,000 per year")
        self.assertEqual(get_salary_range_for_band("mid"), "$40,000–$70,000 per year")
        self.assertEqual(get_salary_range_for_band("senior"), "$70,000–$100,000 per year")
        self.assertEqual(get_salary_range_for_band("unknown"), "")

    def test_job_posting_validation(self):
        # Valid posting
        try:
            JobPosting(
                title="Software Engineer",
                introduction="Join us...",
                role_description="Work on things...",
                responsibilities=["Coding"],
                requirements=["Python"],
                benefits=["Health"],
                salary_range="$40,000–$70,000 per year",
                location="Remote"
            )
        except ValidationError:
            self.fail("JobPosting validation failed unexpectedly")

        # Invalid posting (empty salary_range)
        with self.assertRaises(ValidationError):
            JobPosting(
                title="Software Engineer",
                introduction="Join us...",
                role_description="Work on things...",
                responsibilities=["Coding"],
                requirements=["Python"],
                benefits=["Health"],
                salary_range="",
                location="Remote"
            )

        # Invalid posting (missing salary_range)
        with self.assertRaises(ValidationError):
            JobPosting(
                title="Software Engineer",
                introduction="Join us...",
                role_description="Work on things...",
                responsibilities=["Coding"],
                requirements=["Python"],
                benefits=["Health"],
                location="Remote"
            )

if __name__ == "__main__":
    unittest.main()
