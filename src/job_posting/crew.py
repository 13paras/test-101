from typing import List, Optional
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool
from pydantic import BaseModel, Field

web_search_tool = WebsiteSearchTool()
seper_dev_tool = SerperDevTool()
file_read_tool = FileReadTool(
    file_path='job_description_example.md',
    description='A tool to read the job description example file.'
)

from pydantic import BaseModel, Field, field_validator
import math

class SalaryInfo(BaseModel):
    """Salary information model"""
    salary_min: Optional[float] = Field(None, description="Minimum salary for the role.")
    salary_max: Optional[float] = Field(None, description="Maximum salary for the role.")
    salary_range: Optional[str] = Field(None, description="Formatted salary range string.")

    @field_validator('salary_min', 'salary_max', mode='before')
    @classmethod
    def validate_numbers(cls, v):
        if v is None:
            return None
        try:
            val = float(v)
            if math.isnan(val) or math.isinf(val):
                return None
            return val
        except (ValueError, TypeError):
            return None

    def get_formatted_range(self) -> Optional[str]:
        if self.salary_min is not None and self.salary_max is not None:
            min_val = int(self.salary_min) if self.salary_min.is_integer() else self.salary_min
            max_val = int(self.salary_max) if self.salary_max.is_integer() else self.salary_max
            return f"{min_val} - {max_val}"
        return self.salary_range

class ResearchRoleRequirements(BaseModel):
    """Research role requirements model"""
    skills: List[str] = Field(..., description="List of recommended skills for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    experience: List[str] = Field(..., description="List of recommended experience for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    qualities: List[str] = Field(..., description="List of recommended qualities for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    salary_info: Optional[SalaryInfo] = Field(None, description="Salary information for the role.")

@CrewBase
class JobPostingCrew:
    """JobPosting crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            tools=[web_search_tool, seper_dev_tool],
            verbose=True
        )
    
    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['writer_agent'],
            tools=[web_search_tool, seper_dev_tool, file_read_tool],
            verbose=True
        )
    
    @agent
    def review_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['review_agent'],
            tools=[web_search_tool, seper_dev_tool, file_read_tool],
            verbose=True
        )
    
    @task
    def research_company_culture_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_company_culture_task'],
            agent=self.research_agent()
        )

    @task
    def research_role_requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_role_requirements_task'],
            agent=self.research_agent(),
            output_json=ResearchRoleRequirements
        )

    @task
    def draft_job_posting_task(self) -> Task:
        return Task(
            config=self.tasks_config['draft_job_posting_task'],
            agent=self.writer_agent()
        )

    @task
    def review_and_edit_job_posting_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_and_edit_job_posting_task'],
            agent=self.review_agent()
        )

    @task
    def industry_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['industry_analysis_task'],
            agent=self.research_agent()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the JobPostingCrew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )