import pytest
from job_posting.crew import JobPostingCrew

def test_crew_tasks_have_salary_instructions():
    crew_instance = JobPostingCrew()
    
    # Check research_role_requirements_task
    research_task = crew_instance.research_role_requirements_task()
    assert "salary" in research_task.description.lower()
    assert "salary_info" in research_task.expected_output.lower()
    
    # Check draft_job_posting_task
    draft_task = crew_instance.draft_job_posting_task()
    assert "salary range" in draft_task.description.lower()
    assert "salary range" in draft_task.expected_output.lower()

    # Check review_and_edit_job_posting_task
    review_task = crew_instance.review_and_edit_job_posting_task()
    assert "salary range" in review_task.description.lower()
    assert "salary range" in review_task.expected_output.lower()

def test_research_role_requirements_output_json():
    crew_instance = JobPostingCrew()
    research_task = crew_instance.research_role_requirements_task()
    
    # Verify it uses the updated ResearchRoleRequirements model
    from job_posting.crew import ResearchRoleRequirements
    assert research_task.output_json == ResearchRoleRequirements
    
    # Verify ResearchRoleRequirements has salary_info field
    assert "salary_info" in ResearchRoleRequirements.model_fields
