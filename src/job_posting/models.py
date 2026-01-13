from typing import List
from pydantic import BaseModel, Field, field_validator

class ResearchRoleRequirements(BaseModel):
    """Research role requirements model"""
    skills: List[str] = Field(..., description="List of recommended skills for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    experience: List[str] = Field(..., description="List of recommended experience for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    qualities: List[str] = Field(..., description="List of recommended qualities for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")

class JobPosting(BaseModel):
    """Job posting model"""
    title: str = Field(..., description="The title of the job.")
    introduction: str = Field(..., description="Compelling introduction about the company and the role.")
    role_description: str = Field(..., description="Detailed role description.")
    responsibilities: List[str] = Field(..., description="List of responsibilities.")
    requirements: List[str] = Field(..., description="List of requirements and qualifications.")
    benefits: List[str] = Field(..., description="List of unique company benefits.")
    salary_range: str = Field(..., description="The salary range for the role, e.g., '$40,000–$70,000 per year'. Must be present.")
    location: str = Field(..., description="Location of the job.")

    @field_validator('salary_range')
    @classmethod
    def salary_range_must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError('SalaryRange must be present in job postings')
        return v
