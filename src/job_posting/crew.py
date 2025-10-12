from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import logging

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool
from pydantic import BaseModel, Field
from job_posting.agents.researcher.format_response import (
    format_and_validate_response,
    validate_schema,
    log_error
)

# Configure logging for the crew
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

web_search_tool = WebsiteSearchTool()
seper_dev_tool = SerperDevTool()
file_read_tool = FileReadTool(
    file_path='job_description_example.md',
    description='A tool to read the job description example file.'
)

class ResearchRoleRequirements(BaseModel):
    """Research role requirements model"""
    skills: List[str] = Field(..., description="List of recommended skills for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    experience: List[str] = Field(..., description="List of recommended experience for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")
    qualities: List[str] = Field(..., description="List of recommended qualities for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements.")

def validate_research_output(output):
    """
    Callback function to validate research task output against JSON schema.
    
    This function is called after the research_role_requirements_task completes
    to ensure the output conforms to the expected schema before proceeding.
    """
    logger.info("Validating research task output...")
    
    try:
        # Extract the output data
        if hasattr(output, 'json_dict'):
            output_data = output.json_dict
        elif hasattr(output, 'pydantic'):
            output_data = output.pydantic.dict()
        elif isinstance(output, dict):
            output_data = output
        else:
            output_data = {'raw': str(output)}
            logger.warning(f"Output type not recognized: {type(output)}, attempting to validate raw string")
        
        # Step 4: Validate against JSON schema (as per requirements)
        is_valid = validate_schema(output_data)
        
        # Enhanced logging as per requirements
        if not is_valid:
            log_error("Output does not conform to schema", output_data)
            logger.error("=" * 80)
            logger.error("CRITICAL: Research output validation FAILED")
            logger.error("The output will be passed forward but may cause issues in downstream tasks")
            logger.error("=" * 80)
        else:
            logger.info("✓ Research output validation PASSED - output conforms to schema")
            
    except Exception as e:
        logger.error(f"Error during output validation callback: {e}")
        logger.error("Validation failed but task will continue")
    
    return output


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
        """
        Research role requirements task with integrated output validation.
        
        This task generates research output and validates it against the
        ResearchRoleRequirements JSON schema before passing to downstream tasks.
        """
        task = Task(
            config=self.tasks_config['research_role_requirements_task'],
            agent=self.research_agent(),
            output_json=ResearchRoleRequirements,
            callback=validate_research_output  # Add validation callback
        )
        logger.info("Research task configured with output validation callback")
        return task

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